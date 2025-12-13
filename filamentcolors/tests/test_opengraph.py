import os

import pytest
from PIL import Image

from filamentcolors.tests.helpers import get_swatch


class DummyHtml2Image:
    """Test double for Html2Image.screenshot that avoids launching a browser.

    It records the URL it was asked to screenshot and writes a tiny PNG file
    to the requested `save_as` path so the model code can read it.
    """

    def __init__(self, *args, **kwargs):
        self.requested_urls = []

    def screenshot(self, url: str, save_as: str):
        self.requested_urls.append(url)
        # Create a tiny, valid PNG file for the model to ingest
        img = Image.new("RGB", (1, 1), (255, 0, 0))
        img.save(save_as, format="PNG")
        return [save_as]


@pytest.fixture
def patch_html2image(monkeypatch):
    # Patch the Html2Image class used by the Swatch model
    import filamentcolors.models as models

    dummy = DummyHtml2Image()

    def _factory(*args, **kwargs):
        # Return the same dummy so tests can inspect `requested_urls`
        return dummy

    monkeypatch.setattr(models, "Html2Image", _factory)
    return dummy


def test_create_opengraph_image_uses_id_and_sets_field(patch_html2image, settings):
    # Start with a swatch that has no pre-existing OG image
    swatch = get_swatch(image_opengraph=None)

    # Sanity: field is empty before generation
    assert not swatch.image_opengraph

    # Generate the OpenGraph image (will use the patched Html2Image)
    swatch.create_opengraph_image()

    # Field is populated in-memory
    assert swatch.image_opengraph is not None

    # The temporary file is named using the numeric ID
    expected_basename = f"{swatch.id}-opengraph.png"
    assert os.path.basename(swatch.image_opengraph.name).endswith(expected_basename)

    # The requested URL should point at the ID-based opengraph route
    assert patch_html2image.requested_urls, "Expected screenshot to be requested"
    requested_url = patch_html2image.requested_urls[-1]
    assert f"/swatch/{swatch.id}/opengraph/" in requested_url


def test_get_opengraph_image_generates_when_missing(patch_html2image, db):
    # Create a swatch without an OG image so `get_opengraph_image` must build it
    swatch = get_swatch(image_opengraph=None)

    # Call the helper which regenerates and persists the file
    og_url = swatch.get_opengraph_image()

    # After generation, fetching from DB yields a saved file with a URL
    swatch.refresh_from_db()
    assert swatch.image_opengraph
    assert og_url == swatch.image_opengraph.url
    assert str(swatch.id) in og_url  # URL should include the generated filename with ID

    # Basic sanity: the storage path exists on disk
    assert os.path.exists(swatch.image_opengraph.path)

    # Cleanup the generated file to keep the test media folder tidy
    swatch.image_opengraph.delete(save=False)
