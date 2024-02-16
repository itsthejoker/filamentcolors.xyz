import colorsys
import random
from typing import Any

import numpy
import pandas
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Q
from django.db.models.functions import Lower
from django.http import Http404, HttpResponse
from django.shortcuts import HttpResponseRedirect, reverse
from django.views.decorators.csrf import csrf_exempt
from plotly import graph_objects

from filamentcolors import status
from filamentcolors.colors import (
    convert_short_to_full_hex,
    hex_to_rgb,
    is_hex,
    is_short_hex,
)
from filamentcolors.helpers import (
    ErrorStatusResponse,
    build_data_dict,
    clean_collection_ids,
    generate_custom_library,
    get_custom_library,
    get_hsv,
    get_swatches,
    prep_request,
)
from filamentcolors.models import GenericFilamentType, GenericFile, Manufacturer, Swatch


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
        data["title"] = "Library, sorted by Type"

    elif method == "manufacturer":
        items = items.order_by("manufacturer")
        data["title"] = "Library, sorted by Manufacturer"

    elif method == "random":
        items = list(items)
        random.shuffle(items)
        data["title"] = "Library, sorted by Random"

    elif method == "color":
        items = sorted(items, key=get_hsv)
        data.update({"show_color_warning": True})
        data["title"] = "Library, sorted by Color"

    else:
        items = items.order_by("-date_published")

    data.update({"swatches": items, "show_filter_bar": True})

    return prep_request(request, html, data)


def colorfamilysort(request: WSGIRequest, family_id: str) -> HttpResponse:
    html = "standalone/library.html"
    family_name = [i[1] for i in Swatch.BASE_COLOR_OPTIONS if i[0] == family_id][0]

    data = build_data_dict(request, library=True, title=f"{family_name} Swatches")
    s = get_swatches(data)

    s = s.filter(Q(color_parent=family_id) | Q(alt_color_parent=family_id))

    data.update({"swatches": s})

    return prep_request(request, html, data)


def manufacturersort(request: WSGIRequest, id: int) -> HttpResponse:
    html = "standalone/library.html"
    mfr = Manufacturer.objects.filter(id=id).first()
    if not mfr:
        raise Http404
    data = build_data_dict(request, library=True, title=f"{mfr.name} Swatches")
    s = get_swatches(data)

    s = s.filter(manufacturer=mfr)

    data.update({"swatches": s})

    return prep_request(request, html, data)


def typesort(request: WSGIRequest, id: int) -> HttpResponse:
    html = "standalone/library.html"

    f_type = GenericFilamentType.objects.filter(id=id).first()

    if not f_type:
        raise Http404

    data = build_data_dict(request, library=True, title=f"{f_type.name} Swatches")

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

        data.update(
            {
                "swatch": swatch,
                "title": f"{swatch.manufacturer.name} - {swatch.color_name} {swatch.filament_type.name}",
            }
        )

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
            "title": "View Collection",
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
            "title": "Edit Collection",
        }
    )

    return prep_request(request, html, data)


def inventory_page(request: WSGIRequest) -> HttpResponse:
    data = build_data_dict(request)
    data |= {
        "swatches": Swatch.objects.select_related("manufacturer")
        .prefetch_related("filament_type")
        .order_by(Lower("manufacturer__name"), Lower("color_name")),
        "title": "Inventory",
    }
    data |= {"published_count": data["swatches"].filter(published=True).count()}
    return prep_request(request, "standalone/inventory.html", data)


@csrf_exempt
def colormatch(request: WSGIRequest) -> HttpResponse:
    data = build_data_dict(request, title="Color Match")

    if request.method == "POST":
        incoming_color = request.POST.get("hex_color")
        if not incoming_color:
            # validation is always a good thing
            return ErrorStatusResponse(status=status.HTTP_702_MISSING_COLOR_CODE)
        if is_short_hex(incoming_color):
            incoming_color = convert_short_to_full_hex(incoming_color)
        if not is_hex(incoming_color):
            return ErrorStatusResponse(status=status.HTTP_701_BAD_COLOR_CODE)
        library = get_swatches(data)
        matches = []

        for _ in range(3):
            matching_swatch = Swatch().get_closest_color_swatch(
                library, hex_to_rgb(incoming_color)
            )
            if data["user_settings"].get("show_delta_e_values"):
                distance = matching_swatch.get_distance_to(hex_to_rgb(incoming_color))
            else:
                distance = None

            matches.append([matching_swatch, distance])
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


def swatch_field_visualizer(request: WSGIRequest) -> HttpResponse:
    """Build the swatch visualizer plot originally written by Kevin Rotz."""
    data = build_data_dict(request, title="Swatch Field Visualizer")
    s = get_swatches(data)

    def rgb2hsv(row):
        # convert rgb data in pandas frame into hsv
        hsv = colorsys.rgb_to_hsv(row.rgb_r / 255, row.rgb_g / 255, row.rgb_b / 255)
        return pandas.Series(
            [hsv[0], hsv[1], hsv[2]], index=["hsv_h", "hsv_s", "hsv_v"]
        )

    # https://stackoverflow.com/a/55055351
    values = s.values_list(
        "color_name", "manufacturer__name", "hex_color", "rgb_r", "rgb_g", "rgb_b"
    )

    frame = pandas.DataFrame(
        list(values), columns=["name", "mfr", "hex", "rgb_r", "rgb_g", "rgb_b"]
    )
    frame = frame.join(frame.apply(rgb2hsv, axis=1))
    colors = [
        f"rgb({frame.rgb_r.iloc[i]}, {frame.rgb_g.iloc[i]}, {frame.rgb_b.iloc[i]})"
        for i in range(len(frame))
    ]

    fig = graph_objects.Figure()
    fig = fig.add_trace(
        graph_objects.Scatter3d(
            x=numpy.cos(2 * numpy.pi * frame.hsv_h) * frame.hsv_s,
            y=numpy.sin(2 * numpy.pi * frame.hsv_h) * frame.hsv_s,
            z=frame.hsv_v,
            customdata=numpy.column_stack(
                (
                    frame.rgb_r,
                    frame.rgb_g,
                    frame.rgb_b,
                    frame.hsv_h * 360,
                    frame.hsv_s,
                    frame.hsv_v,
                    frame.hex,
                    frame.mfr,
                )
            ),
            mode="markers",
            marker=dict(color=colors, size=20),
            hovertemplate=(
                "Name: %{text}<br>Brand: %{customdata[7]}"
                "<br>Hex: %{customdata[6]}"
                "<br>RGB: (%{customdata[0]},%{customdata[1]},%{customdata[2]})"
                "<br>HSV: (%{customdata[3]:.2f},%{customdata[4]:.2f},%{customdata[5]:.2f})"
                "<extra></extra>"
            ),
            text=frame.name,
        )
    )
    data["plot"] = fig.to_html(
        full_html=False, include_plotlyjs=False, default_height="800px"
    )

    return prep_request(request, "standalone/visualizer.html", data)


def manufacturer_list(request: WSGIRequest) -> HttpResponse:
    return prep_request(
        request,
        "standalone/manufacturer_list.html",
        build_data_dict(request, title="Manufacturers"),
    )


def about_page(request: WSGIRequest) -> HttpResponse:
    return prep_request(
        request, "standalone/about.html", build_data_dict(request, title="About")
    )


def monetary_donation_page(request: WSGIRequest) -> HttpResponse:
    return prep_request(
        request,
        "standalone/monetary_donations.html",
        build_data_dict(request, title="Monetary Donations"),
    )


def donation_page(request: WSGIRequest) -> HttpResponse:
    return prep_request(
        request,
        "standalone/donations.html",
        build_data_dict(request, title="Donations"),
    )


def error_404(request: WSGIRequest, *args: Any, **kwargs: Any) -> HttpResponse:
    return prep_request(
        request,
        "404.html",
        build_data_dict(request, title="Can't find that..."),
        status=404,
    )


def error_500(request: WSGIRequest, *args: Any, **kwargs: Any) -> HttpResponse:
    return prep_request(
        request,
        "500.html",
        build_data_dict(request, title="Something went wrong!"),
        status=500,
    )


def get_welcome_experience_image(request: WSGIRequest, image_id: int) -> HttpResponse:
    """This is used to serve the welcome experience images."""
    data = build_data_dict(request)

    image = GenericFile.objects.filter(name__icontains=f"step{str(image_id)}").first()
    if not image:
        raise Http404

    data |= {"img_url": image.file.url, "img_alt": image.alt_text}

    return prep_request(
        request,
        f"htmx_partials/welcome_experience_photo.partial",
        data,
    )


def get_welcome_experience_video(request: WSGIRequest) -> HttpResponse:
    """This is used to serve the welcome experience movies."""
    data = build_data_dict(request)

    mp4 = GenericFile.objects.get(
        name__contains="collections_example", file__endswith="mp4"
    )
    webm = GenericFile.objects.get(
        name__contains="collections_example", file__endswith="webm"
    )

    data |= {"mp4_url": mp4.file.url, "webm_url": webm.file.url}

    return prep_request(
        request,
        f"htmx_partials/welcome_experience_video.partial",
        data,
    )
