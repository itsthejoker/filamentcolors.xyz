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
from filamentcolors.tests.ui import scroll_down


@pytest.mark.playwright
@pytest.mark.parametrize(
    "query_param,expected",
    [
        ("3.2-8.8", "TD: 3.2 - 8.8"),
        ("0-8.8", "TD: 0 - 8.8"),
        ("1-100", "TD: 1 - 100"),
        ("0-100", "TD: 0 - 100"),
        ("a-3", "TD"),
        ("3", "TD"),
        ("b", "TD"),
    ],
)
def test_td_loading_from_url(nwo_page, live_server, query_param, expected):
    nwo_page.goto(f"{live_server.url}/library/?td={query_param}")
    expect(nwo_page.locator("#tdFilterModalButton")).to_contain_text(expected)


@pytest.mark.playwright
def test_mfr_loading_from_url(nwo_page, live_server):
    blorbo = get_manufacturer(name="Blorbo")
    swatch = get_swatch(color_name="Green", manufacturer=blorbo)

    nwo_page.goto(f"{live_server.url}/library/?f=&mfr={swatch.manufacturer.slug}")
    expect(nwo_page.locator("#mfrFilterModalButton")).to_contain_text(
        f"{swatch.manufacturer.name}"
    )


@pytest.mark.playwright
def test_mfr_filter_button(nwo_page, live_server):
    blorbo = get_manufacturer(name="Blorbo")
    bleepo = get_manufacturer(name="Bleepo")
    get_swatch(color_name="Blorbo Green", manufacturer=blorbo)
    get_swatch(color_name="Bleepo Blue", manufacturer=bleepo)

    nwo_page.goto(f"{live_server.url}/library/")

    expect(nwo_page.locator(".swatchbox")).to_have_count(2)
    expect(
        nwo_page.locator(".card-text").filter(has_text="Blorbo Green")
    ).to_have_count(1)
    expect(nwo_page.locator(".card-text").filter(has_text="Bleepo Blue")).to_have_count(
        1
    )


@pytest.mark.playwright
def test_mfr_filter_button_pagination(nwo_page, live_server):
    target_mfr = get_manufacturer()  # Defaults to "Tester Materials"
    other_mfr = get_manufacturer(name="Bleepo")

    # Create one early swatch for the target manufacturer that should only appear after pagination
    get_swatch(color_name="Unique Early", manufacturer=target_mfr)

    # Fill the first page with newer swatches from the same manufacturer
    for i in range(settings.PAGINATION_COUNT):
        get_swatch(color_name=f"Page Fill {i + 1}", manufacturer=target_mfr)

    # Create a few swatches for another manufacturer; they should never appear once filtered
    for i in range(3):
        get_swatch(color_name=f"Other {i + 1}", manufacturer=other_mfr)

    nwo_page.goto(f"{live_server.url}/library/")

    # Apply Manufacturer filter via UI
    nwo_page.get_by_role("button", name="Manufacturer").click()
    nwo_page.get_by_label("Filter by Manufacturer").get_by_text(target_mfr.name).click()
    expect(nwo_page.locator("#mfrFilterModalButton")).to_contain_text(target_mfr.name)

    # First page should contain exactly PAGINATION_COUNT swatches, no early item yet
    expect(nwo_page.locator(".swatchbox")).to_have_count(settings.PAGINATION_COUNT)
    expect(
        nwo_page.locator(".card-text").filter(has_text=other_mfr.name)
    ).to_have_count(0)
    expect(
        nwo_page.locator(".card-text").filter(has_text="Unique Early")
    ).to_have_count(0)

    scroll_down(nwo_page)

    # After pagination, the early swatch from the same manufacturer should appear
    expect(nwo_page.locator(".swatchbox")).to_have_count(settings.PAGINATION_COUNT + 1)
    expect(
        nwo_page.locator(".card-text").filter(has_text="Unique Early")
    ).to_have_count(1)
    expect(
        nwo_page.locator(".card-text").filter(has_text=other_mfr.name)
    ).to_have_count(0)


@pytest.mark.playwright
def test_color_family_button(nwo_page, live_server):
    get_swatch(color_name="Black", color_parent=Swatch.BLACK)
    get_swatch(color_name="White", color_parent=Swatch.WHITE)

    nwo_page.goto(f"{live_server.url}/library/")
    expect(nwo_page.locator(".swatchbox")).to_have_count(2)

    nwo_page.get_by_role("button", name="Color Family").click()
    nwo_page.get_by_label("Filter by Color Family").get_by_text("Black").click()
    expect(nwo_page.locator(".swatchbox")).to_have_count(1)
    expect(nwo_page.locator("#deck-of-many-things")).to_contain_text("Black")
    expect(nwo_page.locator("#deck-of-many-things")).not_to_contain_text("White")
    expect(nwo_page.locator("#cfFilterModalButton")).to_contain_text("Black")


@pytest.mark.playwright
def test_color_family_url(nwo_page, live_server):
    get_swatch(color_name="Black", color_parent=Swatch.BLACK)
    get_swatch(color_name="White", color_parent=Swatch.WHITE)

    nwo_page.goto(f"{live_server.url}/library/")
    expect(nwo_page.locator(".swatchbox")).to_have_count(2)

    nwo_page.goto(f"{live_server.url}/library/?f=&cf=white")
    expect(nwo_page.locator(".swatchbox")).to_have_count(1)
    expect(nwo_page.locator("#cfFilterModalButton")).to_contain_text("White")
    expect(nwo_page.locator("#deck-of-many-things")).not_to_contain_text("Black")


@pytest.mark.playwright
def test_filament_type_button(nwo_page, live_server):
    PLA = get_generic_filament_type(name="PLA")
    PETG = get_generic_filament_type(name="PETG")
    PLA2 = get_filament_type(name="PLA-2", parent_type=PLA)
    PETG2 = get_filament_type(name="PETG-2", parent_type=PETG)

    get_swatch(color_name="Black", filament_type=PLA2)
    get_swatch(color_name="White", filament_type=PETG2)

    nwo_page.goto(f"{live_server.url}/library/")
    expect(nwo_page.locator(".swatchbox")).to_have_count(2)

    nwo_page.get_by_role("button", name="Filament Type").click()
    nwo_page.get_by_label("Filter by Filament Type").get_by_text(
        "PLA", exact=True
    ).click()
    expect(nwo_page.locator("#ftFilterModalButton")).to_contain_text("PLA")
    expect(nwo_page.locator(".swatchbox")).to_have_count(1)
    expect(nwo_page.locator("#deck-of-many-things")).not_to_contain_text("PETG-2")


@pytest.mark.playwright
def test_filament_type_url(nwo_page, live_server):
    PLA = get_generic_filament_type(name="PLA")
    PETG = get_generic_filament_type(name="PETG")
    PLA2 = get_filament_type(name="PLA-2", parent_type=PLA)
    PETG2 = get_filament_type(name="PETG-2", parent_type=PETG)

    get_swatch(color_name="Black", filament_type=PLA2)
    get_swatch(color_name="White", filament_type=PETG2)

    nwo_page.goto(f"{live_server.url}/library/")
    expect(nwo_page.locator(".swatchbox")).to_have_count(2)
    nwo_page.goto(f"{live_server.url}/library/?ft=pla")
    expect(nwo_page.locator(".swatchbox")).to_have_count(1)
    expect(nwo_page.locator("#ftFilterModalButton")).to_contain_text("PLA")
    expect(nwo_page.locator("#deck-of-many-things")).to_contain_text("PLA-2")


@pytest.mark.playwright
def test_cf_and_filament_type_combined_ui(nwo_page, live_server):
    PLA = get_generic_filament_type(name="PLA")
    PETG = get_generic_filament_type(name="PETG")
    PLA2 = get_filament_type(name="PLA-2", parent_type=PLA)
    PETG2 = get_filament_type(name="PETG-2", parent_type=PETG)

    get_swatch(color_name="Black-PLA2", color_parent=Swatch.BLACK, filament_type=PLA2)
    get_swatch(color_name="Black-PETG2", color_parent=Swatch.BLACK, filament_type=PETG2)
    get_swatch(color_name="White-PLA2", color_parent=Swatch.WHITE, filament_type=PLA2)

    nwo_page.goto(f"{live_server.url}/library/")
    expect(nwo_page.locator(".swatchbox")).to_have_count(3)

    # First: filter by Color Family (Black)
    nwo_page.get_by_role("button", name="Color Family").click()
    nwo_page.get_by_label("Filter by Color Family").get_by_text("Black").click()
    expect(nwo_page.locator("#cfFilterModalButton")).to_contain_text("Black")
    expect(nwo_page.locator(".swatchbox")).to_have_count(2)

    # Second: add Filament Type (PLA)
    nwo_page.get_by_role("button", name="Filament Type").click()
    nwo_page.get_by_label("Filter by Filament Type").get_by_text(
        "PLA", exact=True
    ).click()
    expect(nwo_page.locator("#ftFilterModalButton")).to_contain_text("PLA")

    # Now only the Black + PLA swatch should remain
    expect(nwo_page.locator(".swatchbox")).to_have_count(1)
    expect(nwo_page.locator("#deck-of-many-things")).to_contain_text("Black-PLA2")
    expect(nwo_page.locator("#deck-of-many-things")).not_to_contain_text("Black-PETG2")
    expect(nwo_page.locator("#deck-of-many-things")).not_to_contain_text("White-PLA2")


@pytest.mark.playwright
def test_cf_and_manufacturer_combined_ui(nwo_page, live_server):
    blorbo = get_manufacturer(name="Blorbo")
    bleepo = get_manufacturer(name="Bleepo")

    get_swatch(
        color_name="Blorbo Black", color_parent=Swatch.BLACK, manufacturer=blorbo
    )
    get_swatch(
        color_name="Bleepo Black", color_parent=Swatch.BLACK, manufacturer=bleepo
    )
    get_swatch(
        color_name="Bleepo White", color_parent=Swatch.WHITE, manufacturer=bleepo
    )

    nwo_page.goto(f"{live_server.url}/library/")
    expect(nwo_page.locator(".swatchbox")).to_have_count(3)

    # First: Color Family → Black (2 results)
    nwo_page.get_by_role("button", name="Color Family").click()
    nwo_page.get_by_label("Filter by Color Family").get_by_text("Black").click()
    expect(nwo_page.locator("#cfFilterModalButton")).to_contain_text("Black")
    expect(nwo_page.locator(".swatchbox")).to_have_count(2)

    # Second: Manufacturer → Blorbo (1 result)
    nwo_page.get_by_role("button", name="Manufacturer").click()
    nwo_page.get_by_label("Filter by Manufacturer").get_by_text(blorbo.name).click()
    expect(nwo_page.locator("#mfrFilterModalButton")).to_contain_text(blorbo.name)

    expect(nwo_page.locator(".swatchbox")).to_have_count(1)
    expect(nwo_page.locator("#deck-of-many-things")).to_contain_text("Blorbo Black")
    expect(nwo_page.locator("#deck-of-many-things")).not_to_contain_text("Bleepo Black")
    expect(nwo_page.locator("#deck-of-many-things")).not_to_contain_text("Bleepo White")


@pytest.mark.playwright
def test_filament_type_and_manufacturer_combined_ui(nwo_page, live_server):
    PLA = get_generic_filament_type(name="PLA")
    PETG = get_generic_filament_type(name="PETG")
    PLA2 = get_filament_type(name="PLA-2", parent_type=PLA)
    PETG2 = get_filament_type(name="PETG-2", parent_type=PETG)
    blorbo = get_manufacturer(name="Blorbo")
    bleepo = get_manufacturer(name="Bleepo")

    get_swatch(color_name="Blorbo PLA-2", filament_type=PLA2, manufacturer=blorbo)
    get_swatch(color_name="Bleepo PLA-2", filament_type=PLA2, manufacturer=bleepo)
    get_swatch(color_name="Bleepo PETG-2", filament_type=PETG2, manufacturer=bleepo)

    nwo_page.goto(f"{live_server.url}/library/")
    expect(nwo_page.locator(".swatchbox")).to_have_count(3)

    # First: Filament Type → PLA (2 results)
    nwo_page.get_by_role("button", name="Filament Type").click()
    nwo_page.get_by_label("Filter by Filament Type").get_by_text(
        "PLA", exact=True
    ).click()
    expect(nwo_page.locator("#ftFilterModalButton")).to_contain_text("PLA")
    expect(nwo_page.locator(".swatchbox")).to_have_count(2)

    # Second: Manufacturer → Blorbo (1 result)
    nwo_page.get_by_role("button", name="Manufacturer").click()
    nwo_page.get_by_label("Filter by Manufacturer").get_by_text(blorbo.name).click()
    expect(nwo_page.locator("#mfrFilterModalButton")).to_contain_text(blorbo.name)

    expect(nwo_page.locator(".swatchbox")).to_have_count(1)
    expect(nwo_page.locator("#deck-of-many-things")).to_contain_text("Blorbo PLA-2")
    expect(nwo_page.locator("#deck-of-many-things")).not_to_contain_text("Bleepo PLA-2")
    expect(nwo_page.locator("#deck-of-many-things")).not_to_contain_text(
        "Bleepo PETG-2"
    )


@pytest.mark.playwright
def test_combined_filters_via_url(nwo_page, live_server):
    PLA = get_generic_filament_type(name="PLA")
    PETG = get_generic_filament_type(name="PETG")
    PLA2 = get_filament_type(name="PLA-2", parent_type=PLA)
    PETG2 = get_filament_type(name="PETG-2", parent_type=PETG)
    blorbo = get_manufacturer(name="Blorbo")
    bleepo = get_manufacturer(name="Bleepo")

    # Target match
    get_swatch(
        color_name="Target Black PLA2 Blorbo",
        color_parent=Swatch.BLACK,
        filament_type=PLA2,
        manufacturer=blorbo,
    )
    # Near misses
    get_swatch(
        color_name="Black PLA2 Bleepo",
        color_parent=Swatch.BLACK,
        filament_type=PLA2,
        manufacturer=bleepo,
    )
    get_swatch(
        color_name="White PLA2 Blorbo",
        color_parent=Swatch.WHITE,
        filament_type=PLA2,
        manufacturer=blorbo,
    )
    get_swatch(
        color_name="Black PETG2 Blorbo",
        color_parent=Swatch.BLACK,
        filament_type=PETG2,
        manufacturer=blorbo,
    )

    nwo_page.goto(f"{live_server.url}/library/?f=&cf=black&ft=pla&mfr={blorbo.slug}")

    # Exactly one result should match all 3 filters
    expect(nwo_page.locator(".swatchbox")).to_have_count(1)
    expect(nwo_page.locator("#cfFilterModalButton")).to_contain_text("Black")
    expect(nwo_page.locator("#ftFilterModalButton")).to_contain_text("PLA")
    expect(nwo_page.locator("#mfrFilterModalButton")).to_contain_text(blorbo.name)
    expect(nwo_page.locator("#deck-of-many-things")).to_contain_text(
        "Target Black PLA2 Blorbo"
    )


@pytest.mark.playwright
def test_combined_filters_with_td_via_url(nwo_page, live_server):
    PLA = get_generic_filament_type(name="PLA")
    PLA2 = get_filament_type(name="PLA-2", parent_type=PLA)
    blorbo = get_manufacturer(name="Blorbo")

    get_swatch(
        color_name="Target Black PLA2 Blorbo",
        color_parent=Swatch.BLACK,
        filament_type=PLA2,
        manufacturer=blorbo,
    )
    get_swatch(
        color_name="White PLA2 Blorbo",
        color_parent=Swatch.WHITE,
        filament_type=PLA2,
        manufacturer=blorbo,
    )

    nwo_page.goto(
        f"{live_server.url}/library/?f=&cf=black&ft=pla&mfr={blorbo.slug}&td=0-100"
    )

    expect(nwo_page.locator(".swatchbox")).to_have_count(1)
    expect(nwo_page.locator("#cfFilterModalButton")).to_contain_text("Black")
    expect(nwo_page.locator("#ftFilterModalButton")).to_contain_text("PLA")
    expect(nwo_page.locator("#mfrFilterModalButton")).to_contain_text(blorbo.name)
    expect(nwo_page.locator("#tdFilterModalButton")).to_contain_text("TD: 0 - 100")
