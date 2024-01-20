from filamentcolors.models import Swatch


def test_affiliate_link_update(swatch: Swatch) -> None:
    swatch.amazon_purchase_link = "https://example.com/aaaaaa/"
    swatch.mfr_purchase_link = "https://example.com/aaa"
    swatch.update_affiliate_links()

    assert (
        swatch.amazon_purchase_link
        == "https://example.com/aaaaaa/?tag=filamentcol0c-20"
    )
    assert swatch.mfr_purchase_link == "https://example.com/aaa?foo=bar"


def test_aff_link_update_with_amzn_shortlink(swatch: Swatch) -> None:
    swatch.amazon_purchase_link = "https://example.com/"
    swatch.update_affiliate_links()
    assert swatch.amazon_purchase_link == "https://example.com/"


def test_aff_links_with_existing_qsps(swatch: Swatch) -> None:
    swatch.amazon_purchase_link = "https://example.com/aaaaaa/?test=hi&hello=world"
    swatch.mfr_purchase_link = "https://example.com/aaa?test=hi&hello=world"
    swatch.update_affiliate_links()
    assert (
        swatch.amazon_purchase_link
        == "https://example.com/aaaaaa/?test=hi&hello=world&tag=filamentcol0c-20"
    )
    assert (
        swatch.mfr_purchase_link
        == "https://example.com/aaa?test=hi&hello=world&foo=bar"
    )


def test_aff_link_already_present(swatch: Swatch) -> None:
    swatch.amazon_purchase_link = "https://example.com/aaaaaa/?tag=filamentcol0c-20"
    swatch.mfr_purchase_link = "https://example.com/aaa?foo=bar"
    swatch.update_affiliate_links()
    assert (
        swatch.amazon_purchase_link
        == "https://example.com/aaaaaa/?tag=filamentcol0c-20"
    )
    assert swatch.mfr_purchase_link == "https://example.com/aaa?foo=bar"