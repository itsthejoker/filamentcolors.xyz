import pytest
from django.conf import settings
from playwright.sync_api import expect

from filamentcolors.tests.helpers import get_manufacturer, get_swatch


@pytest.mark.playwright
def test_manufacturer_route_shows_only_that_manufacturer(nwo_page, live_server):
    target_mfr = get_manufacturer()  # Defaults to "Tester Materials"
    other_mfr = get_manufacturer(name="OtherCo")

    # Create swatches for both manufacturers
    get_swatch(color_name="TM Blue", manufacturer=target_mfr)
    get_swatch(color_name="TM Red", manufacturer=target_mfr)
    get_swatch(color_name="OC Green", manufacturer=other_mfr)
    get_swatch(color_name="OC Blue", manufacturer=other_mfr)

    # Visit manufacturer-specific route
    nwo_page.goto(f"{live_server.url}/library/manufacturer/{target_mfr.slug}/")

    # Only the target manufacturer's swatches should be shown
    expect(nwo_page.locator(".swatchbox")).to_have_count(2)
    expect(
        nwo_page.locator(".card-text").filter(has_text=target_mfr.name)
    ).to_have_count(2)
    expect(
        nwo_page.locator(".card-text").filter(has_text=other_mfr.name)
    ).to_have_count(0)


@pytest.mark.playwright
def test_manufacturer_route_pagination(nwo_page, live_server):
    target_mfr = get_manufacturer()  # Defaults to "Tester Materials"
    other_mfr = get_manufacturer(name="Bleepo")

    # Create one early swatch for the target manufacturer that should only appear after pagination
    get_swatch(color_name="Unique Early", manufacturer=target_mfr)

    # Fill the first page with newer swatches from the same manufacturer
    for i in range(settings.PAGINATION_COUNT):
        get_swatch(color_name=f"Page Fill {i + 1}", manufacturer=target_mfr)

    # Create a few swatches for another manufacturer; they should never appear on this route
    for i in range(3):
        get_swatch(color_name=f"Other {i + 1}", manufacturer=other_mfr)

    nwo_page.goto(f"{live_server.url}/library/manufacturer/{target_mfr.slug}/")

    expect(nwo_page.locator(".swatchbox")).to_have_count(settings.PAGINATION_COUNT)
    expect(
        nwo_page.locator(".card-text").filter(has_text=other_mfr.name)
    ).to_have_count(0)
    expect(
        nwo_page.locator(".card-text").filter(has_text="Unique Early")
    ).to_have_count(0)

    # Trigger infinite scroll pagination
    nwo_page.mouse.wheel(0, 10000)

    # After pagination, one more swatch from the same manufacturer should appear
    expect(nwo_page.locator(".swatchbox")).to_have_count(
        settings.PAGINATION_COUNT + 1
    )
    expect(
        nwo_page.locator(".card-text").filter(has_text="Unique Early")
    ).to_have_count(1)
    expect(
        nwo_page.locator(".card-text").filter(has_text=other_mfr.name)
    ).to_have_count(0)
