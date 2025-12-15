import time

import pytest


def run_on_all_browsers(func):
    """
    Decorator to run a specific test on Chromium, Firefox, and WebKit,
    regardless of the CLI arguments passed to pytest.

    Usage:
        @run_on_all_browsers
        def test_something():
            ...
    """
    return pytest.mark.parametrize("browser_name", ["chromium", "firefox", "webkit"])(
        func
    )


AVOID_WELCOME_OVERLAY_COOKIE = [
    {"name": "f", "value": "tasty_cookies", "domain": "localhost", "path": "/"}
]


def scroll_down(page):
    # if you don't have the sleep call, it fails arbitrarily
    time.sleep(0.3)
    page.mouse.wheel(0, 10000)


def open_settings_modal(page):
    page.get_by_role("list").filter(has_text="Settings").locator("span").click()
    return page.get_by_label("Settings")
