import pytest

from filamentcolors.management.commands import import_pantone_ral
from filamentcolors.models import (
    FilamentType,
    GenericFilamentType,
    Manufacturer,
    Swatch,
)
from filamentcolors.tests.helpers import test_image


def pytest_sessionstart(session):
    """
    Called after the Session object has been created and
    before performing collection and entering the run test loop.
    """
    import_pantone_ral.Command().handle()


@pytest.fixture(autouse=True)
def enable_database_for_all_tests(db) -> None:
    pass


@pytest.fixture
def manufacturer() -> Manufacturer:
    return Manufacturer.objects.get_or_create(
        name="Tester Materials",
        website="",
        swap_purchase_buttons=False,
        affiliate_portal="https://test.test/affiliate",
        affiliate_url_param="&foo=bar",
    )[0]


@pytest.fixture
def generic_filament_type() -> GenericFilamentType:
    return GenericFilamentType.objects.get_or_create(name="Test")[0]


@pytest.fixture
def filament_type(generic_filament_type) -> FilamentType:
    return FilamentType.objects.get_or_create(
        name="Test", parent_type=generic_filament_type
    )[0]


@pytest.fixture
def swatch(manufacturer, filament_type) -> Swatch:
    return Swatch.objects.get_or_create(
        manufacturer=manufacturer,
        hex_color="aabbcc",
        color_name=Swatch.WHITE,
        color_parent=Swatch.WHITE,
        filament_type=filament_type,
        image_front=test_image(),
        image_back=test_image(),
        image_other=test_image(),
    )[0]
