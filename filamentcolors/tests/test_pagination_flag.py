import pytest
from unittest.mock import patch
from django.conf import settings
from filamentcolors.tests.helpers import get_swatch
from filamentcolors.views import librarysort


@pytest.mark.django_db
@patch("filamentcolors.views.prep_request")
def test_librarysort_no_more_flag(prep_mock, rf) -> None:
    # Set up some swatches, but fewer than the pagination count (default 15)
    for i in range(5):
        get_swatch(color_name=f"Swatch {i}")

    request = rf.get("/")
    librarysort(request)

    prep_mock.assert_called_once()
    data = prep_mock.call_args[0][2]

    # Check that the flag is set to True because there's only one page
    assert data.get(settings.FC_NO_MORE) is True
    assert data.get("FC_NO_MORE_CONSTANT") == settings.FC_NO_MORE


@pytest.mark.django_db
@patch("filamentcolors.views.prep_request")
def test_librarysort_has_more_flag_absent(prep_mock, rf) -> None:
    # Set up more than 15 swatches to trigger pagination
    for i in range(20):
        get_swatch(color_name=f"Swatch {i}")

    request = rf.get("/")
    librarysort(request)

    prep_mock.assert_called_once()
    data = prep_mock.call_args[0][2]

    # Check that the flag is NOT set because there are more pages
    assert settings.FC_NO_MORE not in data or data[settings.FC_NO_MORE] is not True
    assert data.get("FC_NO_MORE_CONSTANT") == settings.FC_NO_MORE


@pytest.mark.django_db
def test_api_no_more_flag(client) -> None:
    # API pagination for SmallPageNumberPagination is 15
    for i in range(5):
        get_swatch(color_name=f"Swatch {i}")

    response = client.get("/api/swatch/")
    assert response.status_code == 200
    data = response.json()

    assert data.get(settings.FC_NO_MORE) is True


@pytest.mark.django_db
def test_api_has_more_flag_absent(client) -> None:
    for i in range(20):
        get_swatch(color_name=f"Swatch {i}")

    response = client.get("/api/swatch/")
    assert response.status_code == 200
    data = response.json()

    assert settings.FC_NO_MORE not in data
