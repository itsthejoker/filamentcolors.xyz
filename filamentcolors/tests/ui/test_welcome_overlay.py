import pytest
from playwright.sync_api import expect


@pytest.mark.playwright
def test_popup_overlay_appears_on_first_visit(page, live_server):
    page.goto(f"{live_server.url}/")
    expect(
        page.get_by_role("heading", name="Welcome to FilamentColors.xyz!")
    ).to_be_visible()


@pytest.mark.playwright
def test_popup_overlay_does_not_appear_on_subsequent_visits(page, live_server):
    page.goto(f"{live_server.url}/")
    expect(
        page.get_by_role("heading", name="Welcome to FilamentColors.xyz!")
    ).not_to_be_visible()


@pytest.mark.playwright
def test_closing_overlay_from_done_button(page, live_server):
    page.goto(f"{live_server.url}/")
    expect(
        page.get_by_role("heading", name="Welcome to FilamentColors.xyz!")
    ).to_be_visible()
    page.get_by_role("button", name="Close").nth(1).click()
    expect(
        page.get_by_role("heading", name="Welcome to FilamentColors.xyz!")
    ).not_to_be_visible()


@pytest.mark.playwright
def test_closing_overlay_from_x_button(page, live_server):
    page.goto(f"{live_server.url}/")
    expect(
        page.get_by_role("heading", name="Welcome to FilamentColors.xyz!")
    ).to_be_visible()
    page.get_by_role("button", name="Close").first.click()
    expect(
        page.get_by_role("heading", name="Welcome to FilamentColors.xyz!")
    ).not_to_be_visible()


@pytest.mark.playwright
def test_welcome_experience_button(page, live_server):
    page.goto(f"{live_server.url}/")

    page.get_by_role("dialog", name="Welcome to FilamentColors.xyz!").click()
    page.get_by_label("Welcome to FilamentColors.xyz!").get_by_text(
        "How does this work?"
    ).click()
    expect(page.get_by_role("heading", name="How does this work?")).to_be_visible()

    page.locator("#welcomeExperienceContent").get_by_role("button", name="Next").click()
    expect(page.get_by_role("heading", name="Step 1:")).to_be_visible()

    page.locator("#welcomeExperienceContent").get_by_role("button", name="Next").click()
    expect(page.get_by_role("heading", name="Step 2:")).to_be_visible()

    page.locator("#welcomeExperienceContent").get_by_role("button", name="Next").click()
    expect(page.get_by_role("heading", name="Step 3:")).to_be_visible()

    page.locator("#welcomeExperienceContent").get_by_role("button", name="Next").click()
    expect(page.get_by_role("heading", name="Step 4:")).to_be_visible()

    page.locator("#welcomeExperienceContent").get_by_role("button", name="Next").click()
    expect(
        page.get_by_role("heading", name="Step 5:")
    ).to_be_visible()

    page.locator("#welcomeExperienceContent").get_by_role("button", name="Next").click()
    expect(
        page.get_by_role("heading", name="Step 6:")
    ).to_be_visible()

    page.get_by_role("button", name="Finish").click()
    expect(page.get_by_text("Your comprehensive resource")).to_be_visible()


@pytest.mark.playwright
def test_welcome_experience_back_buttons(page, live_server):
    page.goto(f"{live_server.url}/")

    page.get_by_role("dialog", name="Welcome to FilamentColors.xyz!").click()
    page.get_by_label("Welcome to FilamentColors.xyz!").get_by_text(
        "How does this work?"
    ).click()
    expect(page.get_by_role("heading", name="How does this work?")).to_be_visible()

    page.locator("#welcomeExperienceContent").get_by_role("button", name="Next").click()
    expect(page.get_by_role("heading", name="Step 1:")).to_be_visible()

    page.locator("#welcomeExperienceContent").get_by_role("button", name="Next").click()
    expect(page.get_by_role("heading", name="Step 2:")).to_be_visible()

    page.locator("#welcomeExperienceContent").get_by_role("button", name="Previous").click()
    expect(page.get_by_role("heading", name="Step 1:")).to_be_visible()