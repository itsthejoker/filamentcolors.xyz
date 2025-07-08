from unittest.mock import patch

import pytest

from filamentcolors.tests.helpers import get_purchase_location, get_retailer, get_swatch, get_manufacturer
from filamentcolors.views import librarysort


@patch("filamentcolors.views.prep_request")
def test_librarysort(prep_mock, rf) -> None:
    swatch = get_swatch(color_name="Blue")
    request = rf.get("/")
    librarysort(request)
    prep_mock.assert_called_once()
    swatches = prep_mock.call_args[0][2]['swatches'].object_list
    assert swatch in swatches
    assert len(swatches) == 1


@patch("filamentcolors.views.prep_request")
def test_librarysort_gray_grey_1(prep_mock, rf) -> None:
    # can't easily use parametrize with fixtures. Easier to split this into
    # multiple tests. See https://github.com/pytest-dev/pytest/issues/349
    gray = get_swatch(color_name="Gray")
    grey = get_swatch(color_name="Grey")
    blue = get_swatch(color_name="Blue")
    request = rf.get("/")
    librarysort(request)
    prep_mock.assert_called()
    swatches = prep_mock.call_args[0][2]['swatches'].object_list
    assert len(swatches) == 3
    assert gray in swatches
    assert grey in swatches
    assert blue in swatches


@patch("filamentcolors.views.prep_request")
def test_librarysort_gray_grey_2(prep_mock, rf) -> None:
    gray = get_swatch(color_name="Gray")
    grey = get_swatch(color_name="Grey")
    blue = get_swatch(color_name="Blue")
    request = rf.get("/?f=gray")
    librarysort(request)
    swatches = prep_mock.call_args[0][2]['swatches'].object_list
    assert len(swatches) == 2
    assert gray in swatches
    assert grey in swatches
    assert blue not in swatches


@patch("filamentcolors.views.prep_request")
def test_librarysort_gray_grey_3(prep_mock, rf) -> None:
    gray = get_swatch(color_name="Gray")
    grey = get_swatch(color_name="Grey")
    blue = get_swatch(color_name="Blue")
    request = rf.get("/?f=grey")
    librarysort(request)
    swatches = prep_mock.call_args[0][2]['swatches'].object_list
    assert len(swatches) == 2
    assert gray in swatches
    assert grey in swatches
    assert blue not in swatches


@patch("filamentcolors.views.prep_request")
def test_librarysort_gray_grey_4(prep_mock, rf) -> None:
    gray = get_swatch(color_name="Gray")
    grey = get_swatch(color_name="Grey")
    blue = get_swatch(color_name="Blue")
    request = rf.get("/?f=blue")
    librarysort(request)
    swatches = prep_mock.call_args[0][2]['swatches'].object_list
    assert len(swatches) == 1
    assert gray not in swatches
    assert grey not in swatches
    assert blue in swatches
