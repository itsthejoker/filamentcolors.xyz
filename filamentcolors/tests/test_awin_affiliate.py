import pytest
from django.conf import settings
from filamentcolors.tests.helpers import get_manufacturer, get_swatch


def test_awin_affiliate_link_generation() -> None:
    """Test that Awin affiliate links are correctly generated."""
    mfr = get_manufacturer(awin_affiliate_id="12345", affiliate_url_param=None)
    swatch = get_swatch(manufacturer=mfr, mfr_purchase_link="https://example.com/product")
    
    swatch.update_affiliate_links()
    
    expected_ued = "https%3A%2F%2Fexample.com%2Fproduct"
    assert "https://www.awin1.com/cread.php" in swatch.mfr_purchase_link
    assert "awinmid=12345" in swatch.mfr_purchase_link
    assert f"awinaffid={settings.AWIN_AFFID}" in swatch.mfr_purchase_link
    assert f"ued={expected_ued}" in swatch.mfr_purchase_link


def test_awin_affiliate_link_no_double_wrap() -> None:
    """Test that Awin affiliate links are not wrapped twice."""
    mfr = get_manufacturer(awin_affiliate_id="12345", affiliate_url_param=None)
    initial_link = "https://www.awin1.com/cread.php?awinmid=12345&awinaffid=54321&ued=https%3A%2F%2Fexample.com"
    swatch = get_swatch(manufacturer=mfr, mfr_purchase_link=initial_link)
    
    swatch.update_affiliate_links()
    
    assert swatch.mfr_purchase_link == initial_link


def test_awin_affiliate_link_mfr_link_none() -> None:
    """Test handling when mfr_purchase_link is None."""
    mfr = get_manufacturer(awin_affiliate_id="12345", affiliate_url_param=None)
    swatch = get_swatch(manufacturer=mfr, mfr_purchase_link=None)
    
    # This should no longer crash
    swatch.update_affiliate_links()
    assert swatch.mfr_purchase_link is None


def test_awin_and_affiliate_link_filled_out() -> None:
    """If the awin aff field and the regular aff field are both
    filled out, the awin one should win."""
    mfr = get_manufacturer(awin_affiliate_id="12345", affiliate_url_param="foo=bar")
    swatch = get_swatch(manufacturer=mfr, mfr_purchase_link="https://example.com/product")

    swatch.update_affiliate_links()

    # If Awin wins, the regular affiliate param should NOT be in the link at all
    assert "foo" not in swatch.mfr_purchase_link
    assert "bar" not in swatch.mfr_purchase_link
    assert "awinmid=12345" in swatch.mfr_purchase_link
    assert "https://www.awin1.com/cread.php" in swatch.mfr_purchase_link
