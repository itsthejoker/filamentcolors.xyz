from unittest.mock import patch

import pytest

from filamentcolors.tests.helpers import (
    get_manufacturer,
    get_purchase_location,
    get_retailer,
    get_swatch,
)
from filamentcolors.views import swatch_detail


@patch("filamentcolors.views.prep_request")
def test_swatch_detail(prep_mock, rf) -> None:
    swatch = get_swatch(color_name="Blue")
    request = rf.get(f"/swatch/{swatch.id}/")
    swatch_detail(request, str(swatch.id))
    prep_mock.assert_called_once()
    returned_swatch = prep_mock.call_args[0][2]["swatch"]
    assert returned_swatch == swatch


@patch("filamentcolors.views.prep_request")
def test_swatch_detail_with_redirect(prep_mock, rf) -> None:
    swatch = get_swatch(color_name="Blue")
    green = get_swatch(color_name="Green")
    swatch.replaced_by = green
    swatch.save()
    request = rf.get(f"/swatch/{swatch.id}/")
    swatch_detail(request, str(swatch.id))
    prep_mock.assert_called_once()
    returned_swatch = prep_mock.call_args[0][2]["swatch"]
    assert returned_swatch == green
