import pytest

from filamentcolors.tests.helpers import get_purchase_location, get_retailer, get_swatch, get_manufacturer


# def test_complement() -> None:
#     # todo: broken test
#     blue = get_swatch(hex_color=TestColors.BLUE1)
#     yellow = get_swatch(hex_color=TestColors.YELLOW1)
#     blue.update_all_color_matches(Swatch.objects.all())
#
#     assert blue.complement == yellow


def test_pantone_and_ral_colors_get_automatically_added() -> None:
    swatch = get_swatch()

    assert swatch.closest_pantone_1 is not None
    assert swatch.closest_pantone_2 is not None
    assert swatch.closest_pantone_3 is not None
    assert swatch.closest_ral_1 is not None
    assert swatch.closest_ral_2 is not None
    assert swatch.closest_ral_3 is not None


def test_cropped_images_automatically_added() -> None:
    swatch = get_swatch()

    assert swatch.card_img is not None
    assert swatch.card_img.height == 89
    assert swatch.card_img.width == 288

    assert swatch.image_front is not None
    assert swatch.image_front.height == 2056
    assert swatch.image_front.width == 2740

    assert swatch.image_back is not None
    assert swatch.image_back.height == 2056
    assert swatch.image_back.width == 2740

    # we don't do any special manipulation on the 'other' image,
    # so it should be the same size as it started
    assert swatch.image_other is not None
    assert swatch.image_other.height == 3040
    assert swatch.image_other.width == 4056


def test_affiliate_link_update() -> None:
    swatch = get_swatch()
    swatch.amazon_purchase_link = "https://example.com/aaaaaa/"
    swatch.mfr_purchase_link = "https://example.com/aaa"
    swatch.update_affiliate_links()

    assert (
        swatch.amazon_purchase_link
        == "https://example.com/aaaaaa/?tag=filamentcol0c-20"
    )
    assert swatch.mfr_purchase_link == "https://example.com/aaa?foo=bar"


def test_aff_link_update_with_amzn_shortlink() -> None:
    swatch = get_swatch()
    swatch.amazon_purchase_link = "https://example.com/"
    swatch.update_affiliate_links()
    assert swatch.amazon_purchase_link == "https://example.com/"


def test_aff_links_with_existing_qsps() -> None:
    swatch = get_swatch()
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


def test_aff_link_already_present() -> None:
    swatch = get_swatch()
    swatch.amazon_purchase_link = "https://example.com/aaaaaa/?tag=filamentcol0c-20"
    swatch.mfr_purchase_link = "https://example.com/aaa?foo=bar"
    swatch.update_affiliate_links()
    assert (
        swatch.amazon_purchase_link
        == "https://example.com/aaaaaa/?tag=filamentcol0c-20"
    )
    assert swatch.mfr_purchase_link == "https://example.com/aaa?foo=bar"


def test_aff_link_added_in_purchase_locations() -> None:
    swatch = get_swatch()
    retailer = get_retailer(affiliate_url_param="&hello=world")
    location = get_purchase_location(
        swatch=swatch, retailer=retailer, url="https://example.com"
    )
    swatch.update_affiliate_links()
    location.refresh_from_db()
    assert location.url == "https://example.com?hello=world"
    # now make sure that it doesn't do it twice
    swatch.update_affiliate_links()
    location.refresh_from_db()
    assert location.url == "https://example.com?hello=world"


@pytest.mark.parametrize(
    "mfr_url_param,mfr_purchase_link,expected",
    [
        ("&hello=world", "https://example.com", "https://example.com?hello=world"),
        ("hello=world", "https://example.com", "https://example.com?hello=world"),
        ("?hello=world", "https://example.com", "https://example.com?hello=world"),
        ("?hello=world&", "https://example.com", "https://example.com?hello=world"),
        ("&hello=world", None, None),
        ("hello=world", None, None),
        (None, "https://example.com", "https://example.com"),
        (None, None, None),
        ("&hello=world", "https://example.com?foo=bar", "https://example.com?foo=bar&hello=world"),
        ("&hello=world", "https://example.com?hello=world", "https://example.com?hello=world"),
        ("&hello=world&utm_foo=foo&utm_bar=bar", "https://example.com", "https://example.com?hello=world&utm_foo=foo&utm_bar=bar"),
        ("&hello=world&utm_foo=foo&utm_bar=bar", "https://example.com?utm_foo=foo", "https://example.com?utm_foo=foo&hello=world&utm_bar=bar"),
        ("&hello=world&utm_foo=foo&utm_bar=bar", "https://example.com?something=else", "https://example.com?something=else&hello=world&utm_foo=foo&utm_bar=bar"),
    ]
)
def test_mfr_aff_link(mfr_url_param, mfr_purchase_link, expected) -> None:
    mfr = get_manufacturer(affiliate_url_param=mfr_url_param)
    swatch = get_swatch(manufacturer=mfr, mfr_purchase_link=mfr_purchase_link)
    swatch.update_affiliate_links()
    swatch.refresh_from_db()
    if swatch.mfr_purchase_link:
        assert "??" not in swatch.mfr_purchase_link
    assert swatch.mfr_purchase_link == expected
