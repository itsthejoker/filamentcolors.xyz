from unittest.mock import patch

from filamentcolors.tests.helpers import get_swatch
from filamentcolors.views import inventory_page


@patch("filamentcolors.views.prep_request")
def test_inventory_page(prep_mock, rf) -> None:
    blue = get_swatch(color_name="Blue", published=False)
    green = get_swatch(color_name="Green", published=True)
    request = rf.get("/")
    inventory_page(request)
    prep_mock.assert_called_once()
    swatches = list(prep_mock.call_args[0][2]["swatches"])
    assert blue in swatches
    assert green in swatches
    assert len(swatches) == 2


@patch("filamentcolors.views.prep_request")
def test_inventory_page_with_replaced_swatches(prep_mock, rf) -> None:
    green = get_swatch(color_name="Green", published=True)
    green2 = get_swatch(color_name="kindagreen", published=False)
    request = rf.get("/")
    inventory_page(request)
    prep_mock.assert_called_once()
    swatches = list(prep_mock.call_args[0][2]["swatches"])
    assert green in swatches
    assert green2 in swatches
    assert len(swatches) == 2

    green2.replaced_by = green
    green2.save()
    inventory_page(request)
    swatches = list(prep_mock.call_args[0][2]['swatches'])
    assert len(swatches) == 1
    assert green in swatches
    assert green2 not in swatches
