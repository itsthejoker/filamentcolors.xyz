from unittest.mock import patch

from filamentcolors.tests.helpers import get_swatch
from filamentcolors.views import swatch_collection


@patch("filamentcolors.views.prep_request")
def test_collection_view(prep_mock, rf) -> None:
    swatch1 = get_swatch(color_name="Blue")
    swatch2 = get_swatch(color_name="Green")
    swatch3 = get_swatch(color_name="Red")
    swatch_ids = f"{swatch1.id},{swatch2.id},{swatch3.id}"
    request = rf.get(f"/collections/{swatch_ids}")
    swatch_collection(request, swatch_ids)
    prep_mock.assert_called_once()
    returned_swatches = prep_mock.call_args[0][2]["swatches"].object_list
    assert len(returned_swatches) == 3
    assert swatch1 in returned_swatches
    assert swatch2 in returned_swatches
    assert swatch3 in returned_swatches


@patch("filamentcolors.views.prep_request")
def test_collection_view_with_redirect(prep_mock, rf) -> None:
    swatch1 = get_swatch(color_name="Blue")
    swatch2 = get_swatch(color_name="Green")
    swatch3 = get_swatch(color_name="Red")
    # only request 1 and 2 -- returned values should be 2 and 3
    swatch_ids = f"{swatch1.id},{swatch2.id}"
    swatch1.replaced_by = swatch3
    swatch1.save()
    request = rf.get(f"/collections/{swatch_ids}")
    swatch_collection(request, swatch_ids)
    returned_swatches = prep_mock.call_args[0][2]["swatches"].object_list
    assert len(returned_swatches) == 2
    assert swatch1 not in returned_swatches
    assert swatch2 in returned_swatches
    assert swatch3 in returned_swatches


@patch("filamentcolors.views.prep_request")
def test_collection_view_with_redirect_2(prep_mock, rf) -> None:
    swatch1 = get_swatch(color_name="Blue")
    swatch2 = get_swatch(color_name="Green")
    swatch3 = get_swatch(color_name="Red")
    # Request 1, 2, and 3. 1 is replaced by 3, so we should only get 2 and 3.
    swatch_ids = f"{swatch1.id},{swatch2.id},{swatch3.id}"
    swatch1.replaced_by = swatch3
    swatch1.save()
    request = rf.get(f"/collections/{swatch_ids}")
    swatch_collection(request, swatch_ids)
    returned_swatches = prep_mock.call_args[0][2]["swatches"].object_list
    assert len(returned_swatches) == 2
    assert swatch1 not in returned_swatches
    assert swatch2 in returned_swatches
    assert swatch3 in returned_swatches
