import pytest

from filamentcolors.tests.helpers import get_swatch

API_BASE = "/api/swatch/"


def ids(resp):
    return [r["id"] for r in resp["results"]]


@pytest.mark.django_db
def test_api_respects_id__in_and_does_not_overpaginate(client):
    # Create 5 swatches, pick 3 as a collection
    s_all = [get_swatch(color_name=f"C{i}") for i in range(5)]
    subset = s_all[:3]
    subset_ids = ",".join(str(s.id) for s in subset)

    # Page 1
    p1 = client.get(
        API_BASE,
        {
            "id__in": subset_ids,
            "page": 1,
            "page_size": 2,
            "m": "date",
        },
    ).json()
    assert set(ids(p1)).issubset({s.id for s in subset})
    assert p1["next"] is not None

    # Page 2
    p2 = client.get(
        API_BASE,
        {
            "id__in": subset_ids,
            "page": 2,
            "page_size": 2,
            "m": "date",
        },
    ).json()
    assert set(ids(p2)).issubset({s.id for s in subset})

    # Combined unique ids should be <= 3 and all from subset
    combined = set(ids(p1) + ids(p2))
    assert combined.issubset({s.id for s in subset})

    # Page 3 should be empty (or no next)
    p3_res = client.get(
        API_BASE,
        {
            "id__in": subset_ids,
            "page": 3,
            "page_size": 2,
            "m": "date",
        },
    )
    assert p3_res.status_code == 404  # DRF returns 404 for pages beyond range
