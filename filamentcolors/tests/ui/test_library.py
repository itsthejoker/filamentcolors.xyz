import pytest
from playwright.sync_api import expect

from filamentcolors.models import Swatch
from filamentcolors.tests.helpers import get_swatch, get_manufacturer
from filamentcolors.tests.ui import AVOID_WELCOME_OVERLAY_COOKIE


@pytest.mark.playwright
def test_basic_library_view(nwo_page, live_server):
    swatch = get_swatch(color_name="Blue")

    nwo_page.goto(f"{live_server.url}/library/")
    expect(nwo_page.get_by_role("link", name=f"Card image for {swatch.manufacturer.name}")).to_be_visible()


@pytest.mark.playwright
def test_basic_pagination(nwo_page, live_server):
    get_swatch(color_name="Green")
    for _ in range(15):
        get_swatch(color_name="Blue")

    assert Swatch.objects.first().color_name == "Green"

    nwo_page.goto(f"{live_server.url}/library/")
    expect(nwo_page.locator(".swatchbox")).to_have_count(15)
    expect(nwo_page.locator(".card-text").filter(has_text="Green")).to_have_count(0)

    # trigger pagination
    nwo_page.mouse.wheel(0, 10000)
    expect(nwo_page.locator(".swatchbox")).to_have_count(16)
    expect(nwo_page.locator(".card-text").filter(has_text="Green")).to_have_count(1)


@pytest.mark.playwright
def test_search_by_manufacturer_text(nwo_page, live_server):
    blorbo = get_manufacturer(name="Blorbo")
    makerco = get_manufacturer(name="MakerCo")
    get_swatch(
        color_name="Green", manufacturer=blorbo
    )
    get_swatch(color_name="Blue", manufacturer=makerco)
    nwo_page.goto(f"{live_server.url}/library/")
    nwo_page.get_by_role("textbox", name="Search").click()
    nwo_page.get_by_role("textbox", name="Search").fill("blor")
    expect(nwo_page.locator(".card-text").filter(has_text="Blorbo")).to_have_count(1)
    expect(nwo_page.locator(".card-text").filter(has_text="MakerCo")).to_have_count(0)

    nwo_page.get_by_role("textbox", name="Search").click()
    nwo_page.get_by_role("textbox", name="Search").fill("makerco")
    expect(nwo_page.locator(".card-text").filter(has_text="Blorbo")).to_have_count(0)
    expect(nwo_page.locator(".card-text").filter(has_text="MakerCo")).to_have_count(1)