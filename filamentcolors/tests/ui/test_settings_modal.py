import pytest
from django.conf import settings
from playwright.sync_api import expect

from filamentcolors.tests.helpers import (
    get_filament_type,
    get_generic_filament_type,
    get_manufacturer,
    get_swatch,
)
from filamentcolors.tests.ui import open_settings_modal, scroll_down


@pytest.mark.playwright
def test_settings_page_does_not_save_with_no_filament_types_selected(
    nwo_page, live_server
):
    nwo_page.goto(f"{live_server.url}/library/")

    settings_modal = open_settings_modal(nwo_page)
    scroll_down(nwo_page)

    settings_modal.get_by_text("Exotics").click()
    settings_modal.get_by_text("TPU / TPE").click()
    settings_modal.get_by_text("ABS / ASA").click()
    settings_modal.get_by_text("PETG").click()
    settings_modal.get_by_text("PLA", exact=True).click()
    settings_modal.get_by_role("button", name="Save changes").click()
    expect(nwo_page.locator("body")).to_contain_text(
        "It looks like all filament types have been disabled. Please enable at least one type."
    )
    expect(settings_modal).to_contain_text("Types of filament to display:")


@pytest.mark.playwright
def test_filament_settings_limit_library_with_pagination(nwo_page, live_server):
    """Verify that the limit works across pagination."""
    pla_generic = get_generic_filament_type(name="PLA")
    petg_generic = get_generic_filament_type(name="PETG")
    pla = get_filament_type(name="PLA-2", parent_type=pla_generic)
    petg = get_filament_type(name="PETG-2", parent_type=petg_generic)

    # One early PLA that should only show after pagination
    get_swatch(color_name="Unique Early - PLA", filament_type=pla)

    # Fill the first page with newer PLA swatches
    for i in range(settings.PAGINATION_COUNT):
        get_swatch(color_name=f"Page Fill PLA {i + 1}", filament_type=pla)

    # Add a few PETG swatches that should be hidden once PETG is disabled
    for i in range(3):
        get_swatch(color_name=f"Other PETG {i + 1}", filament_type=petg)

    nwo_page.goto(f"{live_server.url}/library/")

    # Disable PETG in settings
    settings_modal = open_settings_modal(nwo_page)
    settings_modal.get_by_text("PETG").click()
    settings_modal.get_by_role("button", name="Save changes").click()

    # First page shows only PLA swatches, limited to PAGINATION_COUNT
    expect(nwo_page.locator(".swatchbox")).to_have_count(settings.PAGINATION_COUNT)
    expect(nwo_page.locator(".card-text").filter(has_text="PETG-2")).to_have_count(0)
    expect(
        nwo_page.locator(".card-text").filter(has_text="Unique Early - PLA")
    ).to_have_count(0)

    # After pagination, the early PLA appears and PETG is still hidden
    scroll_down(nwo_page)
    expect(nwo_page.locator(".swatchbox")).to_have_count(settings.PAGINATION_COUNT + 1)
    expect(
        nwo_page.locator(".card-text").filter(has_text="Unique Early - PLA")
    ).to_have_count(1)
    expect(nwo_page.locator(".card-text").filter(has_text="PETG-2")).to_have_count(0)


@pytest.mark.playwright
def test_filament_settings_limit_library(nwo_page, live_server):
    pla = get_filament_type(
        name="PLA-2", parent_type=get_generic_filament_type(name="PLA")
    )
    petg = get_filament_type(
        name="PETG-2", parent_type=get_generic_filament_type(name="PETG")
    )
    get_swatch(filament_type=pla, color_name="Green")
    get_swatch(filament_type=petg, color_name="Blue")

    nwo_page.goto(f"{live_server.url}/library/")

    swatchbox = nwo_page.locator(".swatchbox")
    expect(swatchbox).to_have_count(2)

    settings_modal = open_settings_modal(nwo_page)

    settings_modal.get_by_text("PETG").click()
    settings_modal.get_by_role("button", name="Save changes").click()

    expect(swatchbox).to_have_count(1)
    expect(nwo_page.locator(".card-text").filter(has_text="Blue")).to_have_count(0)


@pytest.mark.playwright
def test_show_unavailable_works(nwo_page, live_server):
    green = get_swatch(color_name="Green")
    red = get_swatch(
        color_name="Red", mfr_purchase_link=None, amazon_purchase_link=None
    )

    assert green.is_available()
    assert not red.is_available()

    nwo_page.goto(f"{live_server.url}/library/")
    expect(nwo_page.locator(".swatchbox")).to_have_count(1)

    settings_modal = open_settings_modal(nwo_page)

    settings_modal.get_by_text("Show unavailable filaments").click()
    settings_modal.get_by_role("button", name="Save changes").click()

    swatchbox = nwo_page.locator(".swatchbox")

    expect(swatchbox).to_have_count(2)
    expect(swatchbox.filter(has_text="Unavailable")).to_have_count(1)


@pytest.mark.playwright
def test_show_unavailable_works_with_pagination(nwo_page, live_server):
    """Verify that unavailable swatches works across pagination."""
    # Create one early unavailable swatch
    get_swatch(
        color_name="Unique Early Unavailable",
        mfr_purchase_link=None,
        amazon_purchase_link=None,
    )

    # Fill the first page with newer, available swatches
    for i in range(settings.PAGINATION_COUNT):
        get_swatch(color_name=f"Available {i + 1}")

    nwo_page.goto(f"{live_server.url}/library/")

    # By default, unavailable is hidden; first page should be full of available swatches
    expect(nwo_page.locator(".swatchbox")).to_have_count(settings.PAGINATION_COUNT)
    expect(
        nwo_page.locator(".card-text").filter(has_text="Unique Early Unavailable")
    ).to_have_count(0)

    # Enable 'Show unavailable filaments' in settings
    settings_modal = open_settings_modal(nwo_page)
    settings_modal.get_by_text("Show unavailable filaments").click()
    settings_modal.get_by_role("button", name="Save changes").click()

    # First page still limited; the early unavailable should appear only after pagination
    expect(nwo_page.locator(".swatchbox")).to_have_count(settings.PAGINATION_COUNT)
    expect(nwo_page.locator(".swatchbox").filter(has_text="Unavailable")).to_have_count(
        0
    )

    scroll_down(nwo_page)
    expect(nwo_page.locator(".swatchbox")).to_have_count(settings.PAGINATION_COUNT + 1)
    expect(nwo_page.locator(".swatchbox").filter(has_text="Unavailable")).to_have_count(
        1
    )


@pytest.mark.playwright
def test_cannot_disable_all_manufacturers(nwo_page, live_server):
    tester = get_manufacturer(name="Tester")
    testiferous = get_manufacturer(name="Testiferous")

    # create swatches so that the manufacturers show in the filter
    get_swatch(manufacturer=tester)
    get_swatch(manufacturer=testiferous)

    nwo_page.goto(f"{live_server.url}/library/")

    settings_modal = open_settings_modal(nwo_page)
    settings_modal.get_by_text("Show Advanced").click()

    scroll_down(nwo_page)

    settings_modal.get_by_role("button", name="Unselect All").click()
    settings_modal.get_by_role("button", name="Save changes").click()

    expect(nwo_page.locator("body")).to_contain_text("Please enable at least one.")


@pytest.mark.playwright
def test_disable_single_manufacturer(nwo_page, live_server):
    """Verify that disabling a single manufacturer does not show swatches from that manufacturer."""
    tester = get_manufacturer(name="Tester")
    testiferous = get_manufacturer(name="Testiferous")

    get_swatch(manufacturer=tester)
    get_swatch(manufacturer=testiferous)

    nwo_page.goto(f"{live_server.url}/library/")

    settings_modal = open_settings_modal(nwo_page)
    settings_modal.get_by_text("Show Advanced").click()

    # Manufacturer toggles are farther down in the modal
    scroll_down(nwo_page)

    # Disable Testiferous only
    settings_modal.get_by_text(testiferous.name).click()
    settings_modal.get_by_role("button", name="Save changes").click()

    # Only the "Tester" swatch should remain
    expect(nwo_page.locator(".swatchbox")).to_have_count(1)
    expect(
        nwo_page.locator(".card-text").filter(has_text=testiferous.name)
    ).to_have_count(0)
    expect(nwo_page.locator(".card-text").filter(has_text=tester.name)).to_have_count(1)


@pytest.mark.playwright
def test_disable_single_manufacturer_with_pagination(nwo_page, live_server):
    """Verify that disabling a single manufacturer continues to work across pagination."""
    tester = get_manufacturer(name="Tester")
    testiferous = get_manufacturer(name="Testiferous")

    # One early swatch for allowed manufacturer (Tester) that should appear after pagination
    get_swatch(color_name="Unique Early", manufacturer=tester)

    # Fill the first page with newer swatches for the allowed manufacturer
    for i in range(settings.PAGINATION_COUNT):
        get_swatch(color_name=f"Tester Page Fill {i + 1}", manufacturer=tester)

    # Create a few swatches for the manufacturer we will disable
    for i in range(3):
        get_swatch(color_name=f"Testiferous {i + 1}", manufacturer=testiferous)

    nwo_page.goto(f"{live_server.url}/library/")

    settings_modal = open_settings_modal(nwo_page)
    settings_modal.get_by_text("Show Advanced").click()
    scroll_down(nwo_page)

    # Disable Testiferous
    settings_modal.get_by_text(testiferous.name).click()
    settings_modal.get_by_role("button", name="Save changes").click()

    # First page: limited to PAGINATION_COUNT, no Testiferous, and early item not yet visible
    expect(nwo_page.locator(".swatchbox")).to_have_count(settings.PAGINATION_COUNT)
    expect(
        nwo_page.locator(".card-text").filter(has_text=testiferous.name)
    ).to_have_count(0)
    expect(
        nwo_page.locator(".card-text").filter(has_text="Unique Early")
    ).to_have_count(0)

    # After pagination: the early Tester swatch appears, still no Testiferous
    scroll_down(nwo_page)
    expect(nwo_page.locator(".swatchbox")).to_have_count(settings.PAGINATION_COUNT + 1)
    expect(
        nwo_page.locator(".card-text").filter(has_text="Unique Early")
    ).to_have_count(1)
    expect(
        nwo_page.locator(".card-text").filter(has_text=testiferous.name)
    ).to_have_count(0)
