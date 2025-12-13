import time

import pytest
from django.conf import settings
from playwright.sync_api import expect

from filamentcolors.models import Swatch
from filamentcolors.tests.helpers import (
    get_filament_type,
    get_generic_filament_type,
    get_manufacturer,
    get_swatch,
)


@pytest.mark.playwright
def test_filament_type_route_shows_only_that_type(nwo_page, live_server):
    pla = get_generic_filament_type(name="PLA")
    petg = get_generic_filament_type(name="PETG")
    pla2 = get_filament_type(name="PLA-2", parent_type=pla)
    petg2 = get_filament_type(name="PETG-2", parent_type=petg)

    # Create swatches for both types
    get_swatch(color_name="PLA Black", filament_type=pla2)
    get_swatch(color_name="PLA White", filament_type=pla2)
    get_swatch(color_name="PETG Green", filament_type=petg2)
    get_swatch(color_name="PETG Blue", filament_type=petg2)

    # Visit filament-type specific route (generic type slug)
    nwo_page.goto(f"{live_server.url}/library/filament_type/{pla.slug}/")

    # Only the target type's swatches should be shown
    expect(nwo_page.locator(".swatchbox")).to_have_count(2)
    expect(nwo_page.locator(".card-text").filter(has_text="PLA-2")).to_have_count(2)
    expect(nwo_page.locator(".card-text").filter(has_text="PETG-2")).to_have_count(0)


@pytest.mark.playwright
def test_filament_type_route_pagination(nwo_page, live_server):
    pla = get_generic_filament_type(name="PLA")
    petg = get_generic_filament_type(name="PETG")
    pla2 = get_filament_type(name="PLA-2", parent_type=pla)
    petg2 = get_filament_type(name="PETG-2", parent_type=petg)

    # Create one early swatch for the target type that should only appear after pagination
    get_swatch(color_name="Unique Early - PLA", filament_type=pla2)

    # Fill the first page with newer swatches from the same type
    for i in range(settings.PAGINATION_COUNT):
        get_swatch(color_name=f"Page Fill PLA {i + 1}", filament_type=pla2)

    # Create a few swatches for another type; they should never appear on this route
    for i in range(3):
        get_swatch(color_name=f"Other PETG {i + 1}", filament_type=petg2)

    nwo_page.goto(f"{live_server.url}/library/filament_type/{pla.slug}/")

    expect(nwo_page.locator(".swatchbox")).to_have_count(settings.PAGINATION_COUNT)
    expect(nwo_page.locator(".card-text").filter(has_text="Unique Early - PLA")).to_have_count(0)
    expect(nwo_page.locator(".card-text").filter(has_text="PETG-2")).to_have_count(0)

    # Trigger infinite scroll pagination
    nwo_page.mouse.wheel(0, 10000)

    # After pagination, one more swatch from the same type should appear
    expect(nwo_page.locator(".swatchbox")).to_have_count(settings.PAGINATION_COUNT + 1)
    expect(nwo_page.locator(".card-text").filter(has_text="Unique Early - PLA")).to_have_count(1)
    expect(nwo_page.locator(".card-text").filter(has_text="PETG-2")).to_have_count(0)


@pytest.mark.playwright
def test_filament_type_page_color_family_quick_filter(nwo_page, live_server):
    pla = get_generic_filament_type(name="PLA")
    pla2 = get_filament_type(name="PLA-2", parent_type=pla)

    # Two swatches in the same filament type but different color families
    get_swatch(color_name="Black-PLA2", color_parent=Swatch.BLACK, filament_type=pla2)
    get_swatch(color_name="White-PLA2", color_parent=Swatch.WHITE, filament_type=pla2)

    nwo_page.goto(f"{live_server.url}/library/filament_type/{pla.slug}/")
    expect(nwo_page.locator(".swatchbox")).to_have_count(2)

    # Apply quick filter: Color Family → Black
    nwo_page.get_by_role("button", name="Color Family").click()
    nwo_page.get_by_label("Filter by Color Family").get_by_text("Black").click()

    expect(nwo_page.locator(".swatchbox")).to_have_count(1)
    expect(nwo_page.locator("#deck-of-many-things")).to_contain_text("Black-PLA2")
    expect(nwo_page.locator("#deck-of-many-things")).not_to_contain_text("White-PLA2")
    expect(nwo_page.locator("#cfFilterModalButton")).to_contain_text("Black")


@pytest.mark.playwright
def test_filament_type_page_manufacturer_quick_filter(nwo_page, live_server):
    pla = get_generic_filament_type(name="PLA")
    pla2 = get_filament_type(name="PLA-2", parent_type=pla)

    blorbo = get_manufacturer(name="Blorbo")
    bleepo = get_manufacturer(name="Bleepo")

    # Two swatches in the same filament type but different manufacturers
    get_swatch(color_name="Blorbo Green", filament_type=pla2, manufacturer=blorbo)
    get_swatch(color_name="Bleepo Blue", filament_type=pla2, manufacturer=bleepo)

    nwo_page.goto(f"{live_server.url}/library/filament_type/{pla.slug}/")

    expect(nwo_page.locator(".swatchbox")).to_have_count(2)
    expect(nwo_page.locator(".card-text").filter(has_text="Blorbo Green")).to_have_count(1)
    expect(nwo_page.locator(".card-text").filter(has_text="Bleepo Blue")).to_have_count(1)

    # Apply quick filter: Manufacturer → Blorbo
    nwo_page.get_by_role("button", name="Manufacturer").click()
    nwo_page.get_by_label("Filter by Manufacturer").get_by_text(blorbo.name).click()

    expect(nwo_page.locator("#mfrFilterModalButton")).to_contain_text(blorbo.name)
    expect(nwo_page.locator(".swatchbox")).to_have_count(1)
    expect(nwo_page.locator(".card-text").filter(has_text="Blorbo Green")).to_have_count(1)
    expect(nwo_page.locator(".card-text").filter(has_text="Bleepo Blue")).to_have_count(0)


@pytest.mark.playwright
def test_filament_type_color_family_quick_filter_handles_pagination(
    nwo_page, live_server
):
    """
    On a filament-type-scoped page, applying the Color Family quick filter should
    keep the filter active across infinite-scroll pagination and continue to load
    only swatches matching both the type and the color family.
    """
    pla = get_generic_filament_type(name="PLA")
    pla2 = get_filament_type(name="PLA-2", parent_type=pla)

    # One early black swatch that should appear only after pagination
    get_swatch(color_name="Old Black", color_parent=Swatch.BLACK, filament_type=pla2)

    # Fill the first page with newer Black swatches (same type + color family)
    for i in range(settings.PAGINATION_COUNT):
        get_swatch(
            color_name=f"Fill Black {i + 1}",
            color_parent=Swatch.BLACK,
            filament_type=pla2,
        )

    # Create a few White swatches of the same type; these must never appear after filtering
    for i in range(3):
        get_swatch(
            color_name=f"White {i + 1}", color_parent=Swatch.WHITE, filament_type=pla2
        )

    assert Swatch.objects.count() == 19

    nwo_page.goto(f"{live_server.url}/library/filament_type/{pla.slug}/")

    # Apply quick filter: Color Family → Black
    nwo_page.get_by_role("button", name="Color Family").click()
    nwo_page.get_by_label("Filter by Color Family").get_by_text("Black").click()
    expect(nwo_page.locator("#cfFilterModalButton")).to_contain_text("Black")

    # Before pagination: only page-size Black swatches; "Old Black" not present yet; no Whites
    expect(nwo_page.locator(".swatchbox")).to_have_count(settings.PAGINATION_COUNT)
    expect(nwo_page.locator(".card-text").filter(has_text="Old Black")).to_have_count(0)
    expect(nwo_page.locator(".card-text").filter(has_text="White")).to_have_count(0)

    # Trigger infinite scroll pagination
    time.sleep(0.3)
    nwo_page.mouse.wheel(0, 10000)

    # After pagination: we should see exactly one more Black swatch (the early one)
    expect(nwo_page.locator(".swatchbox")).to_have_count(
        settings.PAGINATION_COUNT + 1
    )
    expect(nwo_page.locator(".card-text").filter(has_text="Old Black")).to_have_count(1)
    expect(nwo_page.locator(".card-text").filter(has_text="White")).to_have_count(0)


@pytest.mark.playwright
def test_filament_type_manufacturer_quick_filter_handles_pagination(
    nwo_page, live_server
):
    """
    On a filament-type-scoped page, applying the Manufacturer quick filter should
    keep the filter active across infinite-scroll pagination and continue to load
    only swatches matching both the type and the manufacturer.
    """
    pla = get_generic_filament_type(name="PLA")
    pla2 = get_filament_type(name="PLA-2", parent_type=pla)

    blorbo = get_manufacturer(name="Blorbo")
    bleepo = get_manufacturer(name="Bleepo")

    # One early Blorbo swatch that should appear only after pagination
    get_swatch(color_name="Old Blorbo", filament_type=pla2, manufacturer=blorbo)

    # Fill the first page with newer Blorbo swatches (same type + manufacturer)
    for i in range(settings.PAGINATION_COUNT):
        get_swatch(
            color_name=f"Fill Blorbo {i + 1}", filament_type=pla2, manufacturer=blorbo
        )

    # Create a few Bleepo swatches of the same type; these must never appear after filtering
    for i in range(3):
        get_swatch(
            color_name=f"Other Bleepo {i + 1}", filament_type=pla2, manufacturer=bleepo
        )

    nwo_page.goto(f"{live_server.url}/library/filament_type/{pla.slug}/")

    # Apply quick filter: Manufacturer → Blorbo
    nwo_page.get_by_role("button", name="Manufacturer").click()
    nwo_page.get_by_label("Filter by Manufacturer").get_by_text(blorbo.name).click()
    expect(nwo_page.locator("#mfrFilterModalButton")).to_contain_text(blorbo.name)

    # Before pagination: only page-size Blorbo swatches; "Old Blorbo" not present yet; no Bleepo
    expect(nwo_page.locator(".swatchbox")).to_have_count(settings.PAGINATION_COUNT)
    expect(nwo_page.locator(".card-text").filter(has_text="Old Blorbo")).to_have_count(0)
    expect(nwo_page.locator(".card-text").filter(has_text=bleepo.name)).to_have_count(0)

    # Trigger infinite scroll pagination
    time.sleep(0.3)
    nwo_page.mouse.wheel(0, 10000)

    # After pagination: we should see exactly one more Blorbo swatch (the early one)
    expect(nwo_page.locator(".swatchbox")).to_have_count(
        settings.PAGINATION_COUNT + 1
    )
    expect(nwo_page.locator(".card-text").filter(has_text="Old Blorbo")).to_have_count(1)
    expect(nwo_page.locator(".card-text").filter(has_text=bleepo.name)).to_have_count(0)
