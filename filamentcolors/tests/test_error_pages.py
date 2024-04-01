from django.test import Client

import pytest


@pytest.mark.urls("filamentcolors.tests.urls")
def test_500_page(client: Client) -> None:
    client.raise_request_exception = False
    response = client.get("/500/")
    assert response.status_code == 500
    assert (
        "Please try your action again -- if it continues to happen"
        in response.content.decode()
    )


@pytest.mark.urls("filamentcolors.tests.urls")
def test_404_page(client: Client) -> None:
    client.raise_request_exception = False
    response = client.get("/404/")
    assert response.status_code == 404
    assert "That page doesn't seem to exist..." in response.content.decode()


@pytest.mark.urls("filamentcolors.tests.urls")
def test_400_page(client: Client) -> None:
    client.raise_request_exception = False
    response = client.get("/400/")
    assert response.status_code == 400
    assert "Did you type the wrong URL?" in response.content.decode()
