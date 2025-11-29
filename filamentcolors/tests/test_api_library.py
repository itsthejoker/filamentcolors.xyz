import itertools

import pytest

from filamentcolors.tests.helpers import (
    get_filament_type,
    get_generic_filament_type,
    get_manufacturer,
    get_swatch,
)

API_BASE = "/api/swatch/"


def ids(resp):
    return [r["id"] for r in resp["results"]]


def get(client, **params):
    return client.get(API_BASE, params).json()


@pytest.mark.django_db
def test_serializer_includes_slug_and_card_img(client):
    s = get_swatch(color_name="Signal Orange")
    data = get(client, id=s.id)
    assert data["count"] >= 1
    item = data["results"][0]
    assert "slug" in item and item["slug"]
    assert "card_img" in item and item["card_img"]


@pytest.mark.django_db
def test_filters_by_manufacturer_slug_and_parent_type_slug(client):
    m1 = get_manufacturer(name="Prusa")
    m2 = get_manufacturer(name="MakerCo")
    g = get_generic_filament_type(name="PLA")
    ft = get_filament_type(name="Prusa-PLA", parent_type=g)
    a = get_swatch(manufacturer=m1, filament_type=ft, color_name="A")
    b = get_swatch(manufacturer=m2, filament_type=ft, color_name="B")

    # manufacturer__slug
    data = get(client, manufacturer__slug=m1.slug)
    assert a.id in ids(data)
    assert b.id not in ids(data)

    # filament_type__parent_type__slug
    data2 = get(client, **{"filament_type__parent_type__slug": g.slug})
    got_ids = ids(data2)
    assert a.id in got_ids and b.id in got_ids


@pytest.mark.django_db
def test_q_and_f_search_gray_grey(client):
    gray = get_swatch(color_name="Gray")
    grey = get_swatch(color_name="Grey")
    blue = get_swatch(color_name="Blue")

    # q=gray should match Gray and Grey, not Blue
    data = get(client, q="gray")
    got = ids(data)
    assert gray.id in got and grey.id in got and blue.id not in got

    # f=grey should match both as well
    data2 = get(client, f="grey")
    got2 = ids(data2)
    assert gray.id in got2 and grey.id in got2 and blue.id not in got2


@pytest.mark.django_db
def test_sort_color_ordering(client):
    # HSV hue order expected: red (0), yellow (~0.166), green (~0.333), blue (~0.666)
    red = get_swatch(color_name="Red", hex_color="FF0000")
    yellow = get_swatch(color_name="Yellow", hex_color="FFFF00")
    green = get_swatch(color_name="Green", hex_color="00FF00")
    blue = get_swatch(color_name="Blue", hex_color="0000FF")

    data = get(client, m="color", page_size=50)
    order = ids(data)
    expected_order = [red.id, yellow.id, green.id, blue.id]

    # Ensure our expected sequence appears in order (not necessarily contiguous if other fixtures exist)
    iter_order = iter(order)
    assert all(x in iter_order for x in expected_order)


@pytest.mark.django_db
def test_random_is_deterministic_within_session_and_changes_across_sessions(client):
    # Create enough swatches for multiple pages
    swatches = [
        get_swatch(color_name=f"C{i}", hex_color=f"{i:02x}{i:02x}{i:02x}")
        for i in range(10, 22)
    ]

    # First session: get page 1 then page 2 with same seed
    p1 = get(client, m="random", page=1, page_size=3)
    p2 = get(client, m="random", page=2, page_size=3)

    # Re-request page 2 within same session should be identical
    p2_repeat = get(client, m="random", page=2, page_size=3)
    assert ids(p2) == ids(p2_repeat)

    # Across different session, order should likely change
    from django.test import Client as DjangoClient

    client2 = DjangoClient()
    p1_other = client2.get(API_BASE, {"m": "random", "page": 1, "page_size": 3}).json()
    p2_other = client2.get(API_BASE, {"m": "random", "page": 2, "page_size": 3}).json()

    # It is acceptable that sometimes the first page overlaps, but combined ordering should usually differ
    assert ids(p1) != ids(p1_other) or ids(p2) != ids(p2_other)

    # Within a session, pages should not have duplicate IDs and should be subsets of all swatches
    all_ids = {s.id for s in swatches}
    assert len(set(ids(p1))) == len(ids(p1))
    assert len(set(ids(p2))) == len(ids(p2))
    assert set(ids(p1)).issubset(all_ids)
    assert set(ids(p2)).issubset(all_ids)
