import pytest
from django.test import Client


@pytest.mark.django_db
@pytest.mark.skip
def test_colormatch_page_get(client: Client) -> None:
    """Test that the colormatch page loads correctly"""
    response = client.get("/colormatch/")
    assert response.status_code == 200
    content = response.content.decode()
    
    # Check that the page contains expected elements
    assert "Color Match" in content
    assert "Color Input" in content
    assert "HEX Color" in content
    assert "RGB Values" in content
    assert "HSV Values" in content
    assert "LAB Values" in content
    assert "Find Matching Colors" in content
    
    # Check for input fields
    assert 'id="hex-input"' in content
    assert 'id="red-input"' in content
    assert 'id="green-input"' in content
    assert 'id="blue-input"' in content
    assert 'id="hue-input"' in content
    assert 'id="saturation-input"' in content
    assert 'id="value-input"' in content
    assert 'id="l-input"' in content
    assert 'id="a-input"' in content
    assert 'id="b-input"' in content
    
    # Check for results section
    assert 'id="results"' in content
    
    # Check for two-column layout
    assert 'col-12 col-lg-5' in content  # Left column for inputs
    assert 'col-12 col-lg-7' in content  # Right column for results
    assert 'Color Input' in content
    assert 'Matching Colors' in content
    
    # Check for rectangular color preview
    assert 'color-preview' in content
    assert 'preview-text' in content
    assert 'Current Color Preview' in content
    
    # Check for grab bag section
    assert 'id="saved_swatches"' in content
    assert 'id="saved_swatches_collection"' in content


@pytest.mark.django_db
def test_colormatch_page_post_with_hex(client: Client) -> None:
    """Test that the colormatch page handles POST requests with HEX color"""
    response = client.post("/colormatch/", {"hex_color": "45FFC1"})
    assert response.status_code == 200
    content = response.content.decode()
    
    # Should return results partial
    assert "Results" in content


@pytest.mark.django_db
def test_colormatch_page_post_with_lab(client: Client) -> None:
    """Test that the colormatch page handles POST requests with LAB values"""
    response = client.post("/colormatch/", {
        "lab_l": "89.973",
        "lab_a": "-58.494", 
        "lab_b": "15.903"
    })
    assert response.status_code == 200
    content = response.content.decode()
    
    # Should return results partial
    assert "Results" in content


@pytest.mark.django_db
def test_colormatch_page_post_missing_color(client: Client) -> None:
    """Test that the colormatch page handles missing color properly"""
    response = client.post("/colormatch/", {})
    assert response.status_code == 702  # HTTP_702_MISSING_COLOR_CODE


@pytest.mark.django_db
def test_colormatch_page_post_invalid_hex(client: Client) -> None:
    """Test that the colormatch page handles invalid HEX color"""
    response = client.post("/colormatch/", {"hex_color": "INVALID"})
    assert response.status_code == 701  # HTTP_701_BAD_COLOR_CODE
