from unittest.mock import patch

from filamentcolors.tests.helpers import get_swatch
from filamentcolors.views import librarysort


@patch("filamentcolors.views.prep_request")
def test_librarysort(prep_mock, rf) -> None:
    swatch = get_swatch(color_name="Blue")
    request = rf.get("/")
    librarysort(request)
    prep_mock.assert_called_once()
    swatches = prep_mock.call_args[0][2]["swatches"].object_list
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
    swatches = prep_mock.call_args[0][2]["swatches"].object_list
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
    swatches = prep_mock.call_args[0][2]["swatches"].object_list
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
    swatches = prep_mock.call_args[0][2]["swatches"].object_list
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
    swatches = prep_mock.call_args[0][2]["swatches"].object_list
    assert len(swatches) == 1
    assert gray not in swatches
    assert grey not in swatches
    assert blue in swatches


@patch("filamentcolors.views.prep_request")
def test_replaced_swatches_not_in_library(prep_mock, rf) -> None:
    swatch = get_swatch(color_name="Blue")
    swatch.replaced_by = get_swatch(color_name="Green")
    swatch.save()
    request = rf.get("/")
    librarysort(request)
    prep_mock.assert_called_once()
    swatches = prep_mock.call_args[0][2]["swatches"].object_list
    assert swatch not in swatches
    assert len(swatches) == 1


@patch("filamentcolors.views.prep_request")
def test_hex_search(prep_mock, rf) -> None:
    # A swatch with a specific color
    # Blue is 0000FF
    swatch = get_swatch(color_name="Blue", hex_color="0000FF")

    # Search for a blue-ish hex code with #
    request = rf.get("/?f=%230000FE")
    librarysort(request)

    prep_mock.assert_called()
    data = prep_mock.call_args[0][2]
    swatches = data["swatches"].object_list

    assert len(swatches) == 1
    assert swatch in swatches
    assert data.get("is_hex_search") is True

    # Search for a short hex code
    request = rf.get("/?f=00F")
    librarysort(request)

    prep_mock.assert_called()
    data = prep_mock.call_args[0][2]
    swatches = data["swatches"].object_list

    assert len(swatches) == 1
    assert swatch in swatches
    assert data.get("is_hex_search") is True


@patch("filamentcolors.views.prep_request")
def test_hex_search_with_color_sort(prep_mock, rf) -> None:
    # Create some swatches
    blue = get_swatch(color_name="Blue", hex_color="0000FF")
    get_swatch(color_name="Red", hex_color="FF0000")

    # Search for a blue-ish hex code while sorting by color
    # This triggers the conversion of items to a list in views.py
    request = rf.get("/?f=%230000FE&m=color")
    librarysort(request)

    prep_mock.assert_called()
    data = prep_mock.call_args[0][2]
    swatches = data["swatches"].object_list

    # Should find the blue swatch and not crash
    assert blue in swatches
    assert data.get("is_hex_search") is True


@patch("filamentcolors.views.prep_request")
def test_hex_search_with_random_sort(prep_mock, rf) -> None:
    # Create some swatches
    get_swatch(color_name="Blue", hex_color="0000FF")
    red = get_swatch(color_name="Red", hex_color="FF0000")

    # Search for a red-ish hex code while sorting by random
    request = rf.get("/?f=%23FE0000&m=random")
    from django.contrib.sessions.middleware import SessionMiddleware

    middleware = SessionMiddleware(lambda r: None)
    middleware.process_request(request)
    request.session.save()

    librarysort(request)

    prep_mock.assert_called()
    data = prep_mock.call_args[0][2]
    swatches = data["swatches"].object_list

    # Should find the red swatch and not crash
    assert red in swatches
    assert data.get("is_hex_search") is True
