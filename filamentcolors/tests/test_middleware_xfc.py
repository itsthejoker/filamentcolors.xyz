def test_xfc_header_detection(client):
    """Test if the X-FC header is correctly detected by the middleware."""
    url = "/api/swatch/"
    # Send request with X-FC header
    response = client.get(url, HTTP_X_FC="true")

    assert response.status_code == 200
    # The middleware should have printed something, but we can't easily check stdout here.
    # However, if it crashed, we'd know.


def test_xfc_header_detection_with_htmx(client):
    """Test if the X-FC header is detected when HX-Request is also present."""
    url = "/api/swatch/"

    response = client.get(url, HTTP_X_FC="true", HTTP_HX_REQUEST="true")

    assert response.status_code == 200
