import atexit
import os

import pytest

from filamentcolors.management.commands import import_pantone_ral
from filamentcolors.tests.ui import AVOID_WELCOME_OVERLAY_COOKIE


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        import_pantone_ral.Command().handle()


@pytest.fixture(autouse=True)
def enable_database_for_all_tests(db) -> None:
    pass


@pytest.fixture
def nwo_page(page):
    """Allows using the `page` fixture without triggering the welcome overlay."""
    page.context.add_cookies(AVOID_WELCOME_OVERLAY_COOKIE)
    return page


# from https://github.com/Chris-May/django_playwright_pytest_example/
def pytest_addoption(parser):
    """Looks for the `runplaywright` argument"""
    parser.addoption(
        "--runplaywright",
        action="store_true",
        default=False,
        help="run playwright tests",
    )


def pytest_configure(config):
    """Auto-add the slow mark to the config at runtime"""
    config.addinivalue_line("markers", "playwright: mark test as slow to run")
    # If running playwright UI tests, enable per-request DB close to avoid
    # sqlite 'unclosed database' warnings from live_server threads.
    if config.getoption("--runplaywright"):
        os.environ["FC_CLOSE_DB_AFTER_REQUEST"] = "1"


def pytest_collection_modifyitems(config, items):
    """This skips the tests if runslow is not present"""
    if config.getoption("--runplaywright"):
        # --runplaywright given in cli: do not skip slow tests
        return
    skip_slow = pytest.mark.skip(reason="need --runplaywright option to run")
    for item in items:
        if "playwright" in item.keywords:
            item.add_marker(skip_slow)


@pytest.fixture(autouse=True)
def allow_unsafe_async():
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


# Ensure all Django DB connections are closed at the very end of the test session.
# This prevents ResourceWarning: unclosed database from sqlite3 when pytest exits.
def pytest_sessionfinish(session, exitstatus):
    try:
        from django.db import connections

        connections.close_all()
    except Exception:
        # Don't let teardown issues mask test results
        pass


def pytest_unconfigure(config):
    """Final safety net to close any lingering Django DB connections."""
    try:
        from django.db import connections

        connections.close_all()
    except Exception:
        pass


@atexit.register
def _close_db_connections_at_exit():
    """Ensure all Django DB connections are closed at interpreter shutdown.

    This is a last-resort guard for sqlite ResourceWarning messages that can
    appear when GC runs after pytest teardown.
    """
    try:
        from django.db import connections

        connections.close_all()
    except Exception:
        pass
