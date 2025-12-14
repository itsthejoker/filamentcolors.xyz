import pytest
from playwright.sync_api import expect

from filamentcolors.tests.helpers import get_swatch


@pytest.mark.playwright
def test_server_loads_at_all(page, live_server):
    page.goto(f"{live_server.url}/admin/")
    page.wait_for_selector("text=Django administration")
    page.fill("[name=username]", "myuser")
    page.fill("[name=password]", "secret")
    page.click("text=Log in")
    assert len(page.eval_on_selector(".errornote", "el => el.innerText")) > 0


@pytest.mark.playwright
def test_clicking_on_swatch_loads_swatch_detail_page(nwo_page, live_server):
    swatch = get_swatch(color_name="Blue")

    nwo_page.goto(f"{live_server.url}/library/")
    nwo_page.locator(".card-click-overlay").first.click()
    nwo_page.get_by_role("columnheader", name="General Info").click()
    expect(nwo_page.get_by_role("columnheader", name="General Info")).to_be_visible()
    expect(nwo_page.get_by_role("heading", name="Matching Colors")).to_be_visible()
    expect(nwo_page.locator("#main")).to_contain_text(
        f"{swatch.manufacturer.name} - {swatch.color_name} {swatch.filament_type.name}"
    )
