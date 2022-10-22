import random
from typing import Any

from django.core.handlers.wsgi import WSGIRequest
from django.http import Http404, HttpResponse
from django.shortcuts import HttpResponseRedirect, reverse

from filamentcolors.helpers import (
    build_data_dict,
    clean_collection_ids,
    generate_custom_library,
    get_custom_library,
    get_hsv,
    get_swatches,
    prep_request,
)
from filamentcolors.models import GenericFilamentType, Swatch


def homepage(request: WSGIRequest) -> HttpResponseRedirect:
    return HttpResponseRedirect(reverse("library"))


def librarysort(request: WSGIRequest, method: str = None) -> HttpResponse:
    """
    Available options:

    'type'
    'date added' <-- default
    'manufacturer'
    'random'
    'color'

    Credit for color sort: https://stackoverflow.com/a/8915267

    :param request: the django request.
    :param method: the string which determines how to sort the results.
    :return:
    """
    html = "standalone/library.html"

    data = build_data_dict(request, library=True)
    items = get_swatches(data)

    if method == "type":
        items = items.order_by("filament_type")

    elif method == "manufacturer":
        items = items.order_by("manufacturer")

    elif method == "random":
        items = list(items)
        random.shuffle(items)

    elif method == "color":
        items = sorted(items, key=get_hsv)
        data.update({"show_color_warning": True})

    else:
        items = items.order_by("-date_added")

    data.update({"swatches": items, "show_filter_bar": True})

    return prep_request(request, html, data)


def colorfamilysort(request: WSGIRequest, family_id: str) -> HttpResponse:
    html = "standalone/library.html"

    data = build_data_dict(request, library=True)
    s = get_swatches(data)

    s = s.filter(color_parent=family_id)

    data.update({"swatches": s})

    return prep_request(request, html, data)


def manufacturersort(request: WSGIRequest, id: int) -> HttpResponse:
    html = "standalone/library.html"

    data = build_data_dict(request, library=True)
    s = get_swatches(data)

    s = s.filter(manufacturer_id=id)

    if len(s) == 0:
        # No filaments found, and we shouldn't have a manufacturer
        # with no filaments.
        raise Http404

    data.update({"swatches": s})

    return prep_request(request, html, data)


def typesort(request: WSGIRequest, id: int) -> HttpResponse:
    html = "standalone/library.html"
    data = build_data_dict(request, library=True)

    f_type = GenericFilamentType.objects.filter(id=id).first()

    if not f_type:
        raise Http404

    s = get_swatches(data)

    s = s.filter(filament_type__parent_type=f_type)

    data.update({"swatches": s})

    return prep_request(request, html, data)


def swatch_detail(request: WSGIRequest, id: int) -> HttpResponse:
    html = "standalone/swatch_detail.html"
    swatch = Swatch.objects.filter(id=id).first()
    data = build_data_dict(request)

    if not swatch or not swatch.published:
        raise Http404
    else:
        swatch.refresh_cache_if_needed()
        if generate_custom_library(data):
            swatch.update_all_color_matches(get_custom_library(data))

        data.update({"swatch": swatch})

        return prep_request(request, html, data)


def swatch_collection(request: WSGIRequest, ids: str) -> HttpResponse:
    data = build_data_dict(request, library=True)

    cleaned_ids = clean_collection_ids(ids)

    swatch_collection = list()

    for item in cleaned_ids:
        result = Swatch.objects.filter(id=item).first()
        if result:
            swatch_collection.append(result)

    data.update(
        {
            "swatches": swatch_collection,
            "collection_ids": ",".join([str(i) for i in cleaned_ids]),
            "show_collection_edit_button": True,
        }
    )

    return prep_request(request, "library.html", data)


def edit_swatch_collection(request: WSGIRequest, ids: str) -> HttpResponse:
    html = "library.html"
    data = build_data_dict(request, library=True)
    cleaned_ids = clean_collection_ids(ids)

    data.update({"preselect_collection": cleaned_ids})
    data.update(
        {
            "swatches": get_swatches(data).order_by("-date_added"),
        }
    )

    return prep_request(request, html, data)


def inventory_page(request: WSGIRequest) -> HttpResponse:
    data = build_data_dict(request)
    data.update(
        {
            "swatches": Swatch.objects.all(),
        }
    )
    return prep_request(request, "inventory.html", data)


def manufacturer_list(request: WSGIRequest) -> HttpResponse:
    return prep_request(
        request, "standalone/manufacturer_list.html", build_data_dict(request)
    )


def about_page(request: WSGIRequest) -> HttpResponse:
    return prep_request(request, "standalone/about.html", build_data_dict(request))


def donation_page(request: WSGIRequest) -> HttpResponse:
    return prep_request(request, "standalone/donations.html", build_data_dict(request))


def error_404(request: WSGIRequest, *args: Any, **kwargs: Any) -> HttpResponse:
    return prep_request(request, "404.html", build_data_dict(request), status=404)


def error_500(request: WSGIRequest, *args: Any, **kwargs: Any) -> HttpResponse:
    return prep_request(request, "500.html", build_data_dict(request), status=500)
