from filamentcolors.tests.helpers import get_swatch, get_purchase_location, get_retailer


# def test_complement() -> None:
#     # todo: broken test
#     blue = get_swatch(hex_color=TestColors.BLUE1)
#     yellow = get_swatch(hex_color=TestColors.YELLOW1)
#     blue.update_all_color_matches(Swatch.objects.all())
#
#     assert blue.complement == yellow


def test_pantone_and_ral_colors_get_automatically_added(
    populate_pantone_and_ral,
) -> None:
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
    assert swatch.card_img.height == 62
    assert swatch.card_img.width == 200

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
