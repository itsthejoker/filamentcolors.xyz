import pytest

from filamentcolors.management.commands import import_pantone_ral


@pytest.fixture()
def populate_pantone_and_ral() -> None:
    import_pantone_ral.Command().handle()


@pytest.fixture(autouse=True)
def enable_database_for_all_tests(db) -> None:
    pass
