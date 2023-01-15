import random
from typing import Any

from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Q
from django.db.models.functions import Lower
from django.http import Http404, HttpResponse
from django.shortcuts import HttpResponseRedirect, reverse
from django.views.decorators.csrf import csrf_exempt

from filamentcolors.colors import hex_to_rgb
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
        items = items.order_by("-date_published")

    data.update({"swatches": items, "show_filter_bar": True})

    return prep_request(request, html, data)


def colorfamilysort(request: WSGIRequest, family_id: str) -> HttpResponse:
    html = "standalone/library.html"

    data = build_data_dict(request, library=True)
    s = get_swatches(data)

    s = s.filter(Q(color_parent=family_id) | Q(alt_color_parent=family_id))

    data.update({"swatches": s})

    return prep_request(request, html, data)


def manufacturersort(request: WSGIRequest, id: int) -> HttpResponse:
    html = "standalone/library.html"

    data = build_data_dict(request, library=True)
    s = get_swatches(data)

    s = s.filter(manufacturer_id=id)

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

    return prep_request(request, "standalone/library.html", data)


def edit_swatch_collection(request: WSGIRequest, ids: str) -> HttpResponse:
    html = "standalone/library.html"
    data = build_data_dict(request, library=True)
    cleaned_ids = clean_collection_ids(ids)

    data.update({"preselect_collection": cleaned_ids})
    data.update(
        {
            "swatches": get_swatches(data).order_by("-date_published"),
        }
    )

    return prep_request(request, html, data)


def inventory_page(request: WSGIRequest) -> HttpResponse:
    data = build_data_dict(request)
    data.update(
        {
            "swatches": Swatch.objects.select_related("manufacturer")
            .prefetch_related("filament_type")
            .order_by(Lower("manufacturer__name"), Lower("color_name")),
        }
    )
    return prep_request(request, "standalone/inventory.html", data)


@csrf_exempt
def colormatch(request: WSGIRequest) -> HttpResponse:
    data = build_data_dict(request)

    if request.method == "POST":
        incoming_color = request.POST.get("hex_color")
        if not incoming_color:
            # validation is always a good thing
            return HttpResponse(status=400)

        library = get_swatches(data)
        matches = []

        for _ in range(3):
            matching_swatch = Swatch().get_closest_color_swatch(
                library, hex_to_rgb(incoming_color)
            )
            matches.append(matching_swatch)
            library = library.exclude(id=matching_swatch.id)

        data["colormatch_swatches"] = matches
        return prep_request(request, "partials/colormatch_results.partial", data)

    return prep_request(request, "standalone/colormatch.html", data)


def single_swatch_card(request: WSGIRequest, swatch_id: int) -> HttpResponse:
    """For the color match page, this is used to populate the 'saved' functionality."""
    data = build_data_dict(request)
    data.update(
        {
            "swatch": Swatch.objects.select_related("manufacturer")
            .prefetch_related("filament_type")
            .get(id=swatch_id),
        }
    )
    return prep_request(request, "partials/single_swatch_column.partial", data)


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
