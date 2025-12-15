"""
Create a set of Playwright tests in the style of `test_mfr_urls.py`. Each of the tests has been stubbed
out in this file. Fill out the test cases to ensure that color pages are being handled correctly. The tests
should be written in a way that each test only tests one concept. Add more tests if needed.

The base color routes are `/library/color_family/{color_slug}/`. The color options are found in
Swatch.BASE_COLOR_OPTIONS.
"""

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
def test_base_color_route_shows_only_that_color(nwo_page, live_server):
    # Target color family: Black; Other color family: White
    get_swatch(color_name="Black One", color_parent=Swatch.BLACK)
    get_swatch(color_name="Black Two", color_parent=Swatch.BLACK)
    get_swatch(color_name="White One", color_parent=Swatch.WHITE)
    get_swatch(color_name="White Two", color_parent=Swatch.WHITE)

    # Visit color-family specific route
    nwo_page.goto(f"{live_server.url}/library/color_family/black/")

    # Only Black swatches should be shown
    expect(nwo_page.locator(".swatchbox")).to_have_count(2)
    expect(nwo_page.locator(".card-text").filter(has_text="Black One")).to_have_count(1)
    expect(nwo_page.locator(".card-text").filter(has_text="Black Two")).to_have_count(1)
    expect(nwo_page.locator(".card-text").filter(has_text="White One")).to_have_count(0)
    expect(nwo_page.locator(".card-text").filter(has_text="White Two")).to_have_count(0)


@pytest.mark.playwright
def test_base_color_route_pagination(nwo_page, live_server):
    # Target color family: Black; Other color family: White
    # Create one early swatch for the target color that should only appear after pagination
    get_swatch(color_name="Unique Early - Black", color_parent=Swatch.BLACK)

    # Fill the first page with newer swatches from the same color family
    for i in range(settings.PAGINATION_COUNT):
        get_swatch(color_name=f"Page Fill Black {i + 1}", color_parent=Swatch.BLACK)

    # Create a few swatches for another color family; they should never appear on this route
    for i in range(3):
        get_swatch(color_name=f"Other White {i + 1}", color_parent=Swatch.WHITE)

    nwo_page.goto(f"{live_server.url}/library/color_family/black/")

    expect(nwo_page.locator(".swatchbox")).to_have_count(settings.PAGINATION_COUNT)
    expect(
        nwo_page.locator(".card-text").filter(has_text="Unique Early - Black")
    ).to_have_count(0)
    expect(nwo_page.locator(".card-text").filter(has_text="Other White")).to_have_count(
        0
    )

    scroll_down(nwo_page)

    # After pagination, one more swatch from the same color family should appear
    expect(nwo_page.locator(".swatchbox")).to_have_count(settings.PAGINATION_COUNT + 1)
    expect(
        nwo_page.locator(".card-text").filter(has_text="Unique Early - Black")
    ).to_have_count(1)
    expect(nwo_page.locator(".card-text").filter(has_text="Other White")).to_have_count(
        0
    )


@pytest.mark.playwright
def test_mfr_quick_filter_on_base_color_route(nwo_page, live_server):
    blorbo = get_manufacturer(name="Blorbo")
    bleepo = get_manufacturer(name="Bleepo")

    # Black swatches for two different manufacturers
    get_swatch(
        color_name="Blorbo Black", manufacturer=blorbo, color_parent=Swatch.BLACK
    )
    get_swatch(
        color_name="Bleepo Black", manufacturer=bleepo, color_parent=Swatch.BLACK
    )
    # Non-target color family should never appear on this route
    get_swatch(
        color_name="Blorbo White", manufacturer=blorbo, color_parent=Swatch.WHITE
    )

    nwo_page.goto(f"{live_server.url}/library/color_family/black/")

    # Only Black family swatches appear initially
    expect(nwo_page.locator(".swatchbox")).to_have_count(2)

    # Apply quick filter: Manufacturer → Blorbo
    nwo_page.get_by_role("button", name="Manufacturer").click()
    nwo_page.get_by_label("Filter by Manufacturer").get_by_text(blorbo.name).click()

    # Button label updates and only Blorbo's Black swatch remains
    expect(nwo_page.locator("#mfrFilterModalButton")).to_contain_text(blorbo.name)
    expect(nwo_page.locator(".swatchbox")).to_have_count(1)
    expect(
        nwo_page.locator(".card-text").filter(has_text="Blorbo Black")
    ).to_have_count(1)
    expect(
        nwo_page.locator(".card-text").filter(has_text="Bleepo Black")
    ).to_have_count(0)


@pytest.mark.playwright
def test_mfr_quick_filter_on_base_color_route_pagination(nwo_page, live_server):
    blorbo = get_manufacturer(name="Blorbo")
    bleepo = get_manufacturer(name="Bleepo")

    # One early Black swatch for Blorbo that should appear only after pagination
    get_swatch(
        color_name="Old Blorbo Black", manufacturer=blorbo, color_parent=Swatch.BLACK
    )

    # Fill the first page with newer Black swatches for Blorbo
    for i in range(settings.PAGINATION_COUNT):
        get_swatch(
            color_name=f"Fill Blorbo Black {i + 1}",
            manufacturer=blorbo,
            color_parent=Swatch.BLACK,
        )

    # Noise: Blacks from other manufacturer and Whites that should never show here
    for i in range(3):
        get_swatch(
            color_name=f"Other Bleepo Black {i + 1}",
            manufacturer=bleepo,
            color_parent=Swatch.BLACK,
        )
    for i in range(3):
        get_swatch(
            color_name=f"Blorbo White {i + 1}",
            manufacturer=blorbo,
            color_parent=Swatch.WHITE,
        )

    nwo_page.goto(f"{live_server.url}/library/color_family/black/")

    # Apply quick filter: Manufacturer → Blorbo
    nwo_page.get_by_role("button", name="Manufacturer").click()
    nwo_page.get_by_label("Filter by Manufacturer").get_by_text(blorbo.name).click()
    expect(nwo_page.locator("#mfrFilterModalButton")).to_contain_text(blorbo.name)

    # Before pagination: page-size Blorbo Blacks; early one not present; no Bleepo
    expect(nwo_page.locator(".swatchbox")).to_have_count(settings.PAGINATION_COUNT)
    expect(
        nwo_page.locator(".card-text").filter(has_text="Old Blorbo Black")
    ).to_have_count(0)
    expect(nwo_page.locator(".card-text").filter(has_text="Bleepo")).to_have_count(0)

    scroll_down(nwo_page)

    # After pagination: exactly one more Blorbo Black swatch (the early one)
    expect(nwo_page.locator(".swatchbox")).to_have_count(settings.PAGINATION_COUNT + 1)
    expect(
        nwo_page.locator(".card-text").filter(has_text="Old Blorbo Black")
    ).to_have_count(1)
    expect(nwo_page.locator(".card-text").filter(has_text="Bleepo")).to_have_count(0)


@pytest.mark.playwright
def test_filament_type_quick_filter_on_base_color_route(nwo_page, live_server):
    # Create two generic filament types and child types
    pla = get_generic_filament_type(name="PLA")
    petg = get_generic_filament_type(name="PETG")
    pla2 = get_filament_type(name="PLA-2", parent_type=pla)
    petg2 = get_filament_type(name="PETG-2", parent_type=petg)

    # Black swatches across two types; a White swatch that shouldn't appear on Black route
    get_swatch(color_name="Black-PLA2", color_parent=Swatch.BLACK, filament_type=pla2)
    get_swatch(color_name="Black-PETG2", color_parent=Swatch.BLACK, filament_type=petg2)
    get_swatch(color_name="White-PLA2", color_parent=Swatch.WHITE, filament_type=pla2)

    nwo_page.goto(f"{live_server.url}/library/color_family/black/")

    # Only Black family swatches appear initially
    expect(nwo_page.locator(".swatchbox")).to_have_count(2)

    # Apply quick filter: Filament Type → PLA
    nwo_page.get_by_role("button", name="Filament Type").click()
    nwo_page.get_by_label("Filter by Filament Type").get_by_text(pla.name).click()

    # Button label updates and only PLA's Black swatch remains
    expect(nwo_page.locator("#ftFilterModalButton")).to_contain_text(pla.name)
    expect(nwo_page.locator(".swatchbox")).to_have_count(1)
    expect(nwo_page.locator(".card-text").filter(has_text="PLA-2")).to_have_count(1)
    expect(nwo_page.locator(".card-text").filter(has_text="PETG-2")).to_have_count(0)


@pytest.mark.playwright
def test_filament_type_quick_filter_on_base_color_route_pagination(
    nwo_page, live_server
):
    # Create two generic filament types and child types
    pla = get_generic_filament_type(name="PLA")
    petg = get_generic_filament_type(name="PETG")
    pla2 = get_filament_type(name="PLA-2", parent_type=pla)
    petg2 = get_filament_type(name="PETG-2", parent_type=petg)

    # One early Black swatch for PLA that should appear only after pagination
    get_swatch(
        color_name="Old PLA Black", color_parent=Swatch.BLACK, filament_type=pla2
    )

    # Fill the first page with newer Black swatches for PLA
    for i in range(settings.PAGINATION_COUNT):
        get_swatch(
            color_name=f"Fill PLA Black {i + 1}",
            color_parent=Swatch.BLACK,
            filament_type=pla2,
        )

    # Noise: Blacks from other type and Whites that should never show here after filtering
    for i in range(3):
        get_swatch(
            color_name=f"Other PETG Black {i + 1}",
            color_parent=Swatch.BLACK,
            filament_type=petg2,
        )
    for i in range(3):
        get_swatch(
            color_name=f"PLA White {i + 1}",
            color_parent=Swatch.WHITE,
            filament_type=pla2,
        )

    nwo_page.goto(f"{live_server.url}/library/color_family/black/")

    # Apply quick filter: Filament Type → PLA
    nwo_page.get_by_role("button", name="Filament Type").click()
    nwo_page.get_by_label("Filter by Filament Type").get_by_text(pla.name).click()
    expect(nwo_page.locator("#ftFilterModalButton")).to_contain_text(pla.name)

    # Before pagination: page-size PLA Blacks; early one not present; no PETG
    expect(nwo_page.locator(".swatchbox")).to_have_count(settings.PAGINATION_COUNT)
    expect(
        nwo_page.locator(".card-text").filter(has_text="Old PLA Black")
    ).to_have_count(0)
    expect(nwo_page.locator(".card-text").filter(has_text="PETG-2")).to_have_count(0)

    scroll_down(nwo_page)

    # After pagination: exactly one more PLA Black swatch (the early one)
    expect(nwo_page.locator(".swatchbox")).to_have_count(settings.PAGINATION_COUNT + 1)
    expect(
        nwo_page.locator(".card-text").filter(has_text="Old PLA Black")
    ).to_have_count(1)
    expect(nwo_page.locator(".card-text").filter(has_text="PETG-2")).to_have_count(0)


@pytest.mark.playwright
def test_filter_on_base_color_route(nwo_page, live_server):
    blorbo = get_manufacturer(name="Blorbo")
    bleepo = get_manufacturer(name="Bleepo")

    # Black swatches for two different manufacturers
    get_swatch(
        color_name="Blorbo Black", manufacturer=blorbo, color_parent=Swatch.BLACK
    )
    get_swatch(
        color_name="Bleepo Black", manufacturer=bleepo, color_parent=Swatch.BLACK
    )
    # Non-target color family that matches the text query should never appear on this route
    get_swatch(
        color_name="Blorbo White", manufacturer=blorbo, color_parent=Swatch.WHITE
    )

    nwo_page.goto(f"{live_server.url}/library/color_family/black/")

    # Only Black family swatches appear initially
    expect(nwo_page.locator(".swatchbox")).to_have_count(2)

    # Use the normal search filter (free-text) to narrow to manufacturer "Blorbo"
    nwo_page.get_by_role("textbox", name="Search").click()
    nwo_page.get_by_role("textbox", name="Search").fill("blor")

    # Only Blorbo's Black swatch should remain; Bleepo and any Whites should not appear
    expect(nwo_page.locator(".swatchbox")).to_have_count(1)
    expect(
        nwo_page.locator(".card-text").filter(has_text="Blorbo Black")
    ).to_have_count(1)
    expect(
        nwo_page.locator(".card-text").filter(has_text="Bleepo Black")
    ).to_have_count(0)


@pytest.mark.playwright
def test_filter_on_base_color_route_pagination(nwo_page, live_server):
    blorbo = get_manufacturer(name="Blorbo")
    bleepo = get_manufacturer(name="Bleepo")

    # One early Black swatch for Blorbo that should appear only after pagination
    get_swatch(
        color_name="Old Blorbo Black", manufacturer=blorbo, color_parent=Swatch.BLACK
    )

    # Fill the first page with newer Black swatches for Blorbo (match the text query)
    for i in range(settings.PAGINATION_COUNT):
        get_swatch(
            color_name=f"Fill Blorbo Black {i + 1}",
            manufacturer=blorbo,
            color_parent=Swatch.BLACK,
        )

    # Noise: Blacks from other manufacturer and Whites that should never show here
    for i in range(3):
        get_swatch(
            color_name=f"Other Bleepo Black {i + 1}",
            manufacturer=bleepo,
            color_parent=Swatch.BLACK,
        )
    for i in range(3):
        get_swatch(
            color_name=f"Blorbo White {i + 1}",
            manufacturer=blorbo,
            color_parent=Swatch.WHITE,
        )

    nwo_page.goto(f"{live_server.url}/library/color_family/black/")

    # Apply the normal text search: filter by manufacturer text "blor"
    nwo_page.get_by_role("textbox", name="Search").click()
    nwo_page.get_by_role("textbox", name="Search").fill("blor")

    # Before pagination: page-size Blorbo Blacks; early one not present; no Bleepo
    expect(nwo_page.locator(".swatchbox")).to_have_count(settings.PAGINATION_COUNT)
    expect(
        nwo_page.locator(".card-text").filter(has_text="Old Blorbo Black")
    ).to_have_count(0)
    expect(nwo_page.locator(".card-text").filter(has_text="Bleepo")).to_have_count(0)

    scroll_down(nwo_page)

    # After pagination: exactly one more Blorbo Black swatch (the early one)
    expect(nwo_page.locator(".swatchbox")).to_have_count(settings.PAGINATION_COUNT + 1)
    expect(
        nwo_page.locator(".card-text").filter(has_text="Old Blorbo Black")
    ).to_have_count(1)
    expect(nwo_page.locator(".card-text").filter(has_text="Bleepo")).to_have_count(0)


@pytest.mark.playwright
def test_td_filter_on_base_color_route(nwo_page, live_server):
    # Create Black swatches with various TD values and a White swatch for noise
    get_swatch(color_name="Black TD 5", color_parent=Swatch.BLACK, td=5.0)
    get_swatch(color_name="Black TD 15", color_parent=Swatch.BLACK, td=15.0)
    get_swatch(color_name="Black TD 60", color_parent=Swatch.BLACK, td=60.0)
    get_swatch(color_name="White TD 15", color_parent=Swatch.WHITE, td=15.0)

    nwo_page.goto(f"{live_server.url}/library/color_family/black/")

    # Apply TD quick filter using the Text tab to target only TD in [10, 20]
    nwo_page.get_by_role("button", name="TD").click()
    nwo_page.locator("#tdTextTab").click()
    nwo_page.locator("#tdMinTextInput").fill("10")
    nwo_page.locator("#tdMaxTextInput").fill("20")
    nwo_page.locator("#selectTdFilter").click()

    # Button label updates and only the Black swatch within range remains
    expect(nwo_page.locator("#tdFilterModalButton")).to_contain_text("TD: 10 - 20")
    expect(nwo_page.locator(".swatchbox")).to_have_count(1)
    expect(nwo_page.locator(".card-text").filter(has_text="Black TD 15")).to_have_count(
        1
    )
    expect(nwo_page.locator(".card-text").filter(has_text="Black TD 5")).to_have_count(
        0
    )
    expect(nwo_page.locator(".card-text").filter(has_text="Black TD 60")).to_have_count(
        0
    )
    # White swatches should never appear on the Black route
    expect(nwo_page.locator(".card-text").filter(has_text="White TD 15")).to_have_count(
        0
    )


@pytest.mark.playwright
def test_td_filter_on_base_color_route_pagination(nwo_page, live_server):
    # One early Black swatch within TD range that should appear only after pagination
    get_swatch(color_name="Old Black TD 15", color_parent=Swatch.BLACK, td=15.0)

    # Fill the first page with newer Black swatches within the same TD range
    for i in range(settings.PAGINATION_COUNT):
        get_swatch(
            color_name=f"Fill Black TD 15 {i + 1}",
            color_parent=Swatch.BLACK,
            td=15.0,
        )

    # Noise: Blacks outside the TD range and Whites that should never show here
    for i in range(3):
        get_swatch(
            color_name=f"Other Black TD {i + 1}",
            color_parent=Swatch.BLACK,
            td=2.0,
        )
    for i in range(3):
        get_swatch(
            color_name=f"White TD 15 {i + 1}",
            color_parent=Swatch.WHITE,
            td=15.0,
        )

    nwo_page.goto(f"{live_server.url}/library/color_family/black/")

    # Apply TD quick filter using the Text tab to target TD in [10, 20]
    nwo_page.get_by_role("button", name="TD").click()
    nwo_page.locator("#tdTextTab").click()
    nwo_page.locator("#tdMinTextInput").fill("10")
    nwo_page.locator("#tdMaxTextInput").fill("20")
    nwo_page.locator("#selectTdFilter").click()
    expect(nwo_page.locator("#tdFilterModalButton")).to_contain_text("TD: 10 - 20")

    # Before pagination: page-size Blacks within TD range; early one not present; no Whites or out-of-range
    expect(nwo_page.locator(".swatchbox")).to_have_count(settings.PAGINATION_COUNT)
    expect(
        nwo_page.locator(".card-text").filter(has_text="Old Black TD 15")
    ).to_have_count(0)
    expect(nwo_page.locator(".card-text").filter(has_text="White TD 15")).to_have_count(
        0
    )
    expect(
        nwo_page.locator(".card-text").filter(has_text="Other Black TD")
    ).to_have_count(0)

    scroll_down(nwo_page)

    # After pagination: exactly one more Black swatch (the early one) appears
    expect(nwo_page.locator(".swatchbox")).to_have_count(settings.PAGINATION_COUNT + 1)
    expect(
        nwo_page.locator(".card-text").filter(has_text="Old Black TD 15")
    ).to_have_count(1)
    expect(nwo_page.locator(".card-text").filter(has_text="White TD 15")).to_have_count(
        0
    )
    expect(
        nwo_page.locator(".card-text").filter(has_text="Other Black TD")
    ).to_have_count(0)


@pytest.mark.playwright
def test_clear_filters_button_does_not_show_on_base_color_route(nwo_page, live_server):
    # Seed some swatches; only Blacks should render on the Black route
    get_swatch(color_name="Black One", color_parent=Swatch.BLACK)
    get_swatch(color_name="Black Two", color_parent=Swatch.BLACK)
    get_swatch(color_name="White Noise", color_parent=Swatch.WHITE)

    nwo_page.goto(f"{live_server.url}/library/color_family/black/")

    # Sanity: only Black swatches shown
    expect(nwo_page.locator(".swatchbox")).to_have_count(2)

    # The Clear Active Filters button should not be visible on a color-family-scoped route
    # when no user-applied filters are active (page-level constraint doesn't count).
    expect(nwo_page.locator("#clearAllFiltersButton")).to_be_hidden()
