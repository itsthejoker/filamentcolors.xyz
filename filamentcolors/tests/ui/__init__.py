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
