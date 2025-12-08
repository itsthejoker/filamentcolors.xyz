import pytest
from playwright.sync_api import expect

from filamentcolors.tests.helpers import get_manufacturer, get_swatch


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

    nwo_page.get_by_role("button", name="Manufacturer").click()
    nwo_page.get_by_label("Filter by Manufacturer").get_by_text(blorbo.name).click()
    expect(nwo_page.locator("#mfrFilterModalButton")).to_contain_text(blorbo.name)

    expect(nwo_page.locator(".swatchbox")).to_have_count(1)
    expect(
        nwo_page.locator(".card-text").filter(has_text="Blorbo Green")
    ).to_have_count(1)
    expect(nwo_page.locator(".card-text").filter(has_text="Bleepo Blue")).to_have_count(
        0
    )
