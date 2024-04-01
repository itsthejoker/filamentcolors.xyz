import pytest

from filamentcolors.management.commands import import_pantone_ral


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        import_pantone_ral.Command().handle()


@pytest.fixture(autouse=True)
def enable_database_for_all_tests(db) -> None:
    pass
