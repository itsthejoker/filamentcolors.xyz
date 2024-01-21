import pytest

from filamentcolors.management.commands import import_pantone_ral


def pytest_sessionstart(session):
    """
    Called after the Session object has been created and
    before performing collection and entering the run test loop.
    """
    import_pantone_ral.Command().handle()


@pytest.fixture(autouse=True)
def enable_database_for_all_tests(db) -> None:
    pass
