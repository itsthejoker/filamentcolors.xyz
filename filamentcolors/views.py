import colorsys
import json
import random
from typing import Any

import numpy
import pandas
from django.http import HttpRequest
from django.contrib import messages
from django.db.models import Q, QuerySet
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
from filamentcolors.exceptions import UnknownSlugOrID
from filamentcolors.helpers import (
    ErrorStatusResponse,
    build_data_dict,
    clean_collection_ids,
    generate_custom_library,
    get_custom_library,
    get_hsv,
    get_swatches,
    prep_request,
    is_infinite_scroll_request,
    get_swatch_paginator,
    is_searchbar_request,
    get_new_seed,
)
from filamentcolors.models import (
    GenericFilamentType,
    GenericFile,
    Manufacturer,
    Swatch,
    DeadLink,
)


def homepage(request: HttpRequest) -> HttpResponseRedirect:
    return HttpResponseRedirect(reverse("library"))


#   _________                __         .__      _________                  .___
#  /   _____/_  _  _______ _/  |_  ____ |  |__   \_   ___ \_____ _______  __| _/______
#  \_____  \\ \/ \/ /\__  \\   __\/ ___\|  |  \  /    \  \/\__  \\_  __ \/ __ |/  ___/
#  /        \\     /  / __ \|  | \  \___|   Y  \ \     \____/ __ \|  | \/ /_/ |\___ \
# /_______  / \/\_/  (____  /__|  \___  >___|  /  \______  (____  /__|  \____ /____  >
#         \/              \/          \/     \/          \/     \/           \/    \/


def librarysort(
    request: HttpRequest,
    method: str = None,
    library: QuerySet[Swatch] = None,
    prebuilt_data: dict = None,
) -> HttpResponse:
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
    :param library: the queryset of swatches to sort. Optional.
    :param prebuilt_data: the data dict to use. Optional.
    :return:
    """
    html = "standalone/library.html"
    data = prebuilt_data if prebuilt_data else build_data_dict(request, library=True)
    if isinstance(library, QuerySet):
        items = library
    else:
        items = get_swatches(data)
    filter_str = request.GET.get("f", None)
    color_family_str = request.GET.get("cf", None)
    mfr_str = request.GET.get("mfr", None)
    f_type_str = request.GET.get("ft", None)
    td_range = request.GET.get("td", None)

    if filter_str == "null":
        filter_str = None

    if not method:
        method = request.GET.get("m", None)

    if filter_str:
        split_filter_str = filter_str.strip().lower().split()
        data.update({"search_prefill": filter_str})
        for section in split_filter_str:
            items = items.filter(
                Q(color_name__icontains=section)
                | Q(manufacturer__name__icontains=section)
                | Q(filament_type__name__icontains=section)
            )

    if color_family_str:
        try:
            f_id = Swatch().get_color_id_from_slug_or_id(color_family_str)
        except UnknownSlugOrID:
            raise Http404

        items = items.filter(Q(color_parent=f_id) | Q(alt_color_parent=f_id))

    if mfr_str:
        try:
            mfr_id = Manufacturer().get_slug_from_id_or_slug(mfr_str)
        except Manufacturer.DoesNotExist:
            raise Http404

        items = items.filter(manufacturer__slug=mfr_id)

    if f_type_str:
        try:
            int(f_type_str)  # will explode if it's not an int
            items = items.filter(filament_type__parent_type__id=f_type_str)
        except ValueError:
            items = items.filter(filament_type__parent_type__slug=f_type_str)

    if td_range:
        # It should be in the format of 0-100 (min dash max)
        try:
            min_td, max_td = list(map(float, td_range.split("-")))
        except ValueError:
            min_td, max_td = 0, 100

        items = items.filter(calculated_td__gte=min_td, calculated_td__lte=max_td)

    if method == "type":
        items = items.order_by("filament_type")
        data["title"] = "Library, sorted by Type"

    elif method == "manufacturer":
        items = items.order_by("manufacturer")
        data["title"] = "Library, sorted by Manufacturer"

    elif method == "random":
        if is_infinite_scroll_request(request):
            # we're getting a paginated entry, not requesting the page for the first time.
            seed = request.session.get("random_seed", get_new_seed())
        else:
            # we're getting the page for the first time. Forcibly create a new seed.
            seed = get_new_seed()
            request.session["random_seed"] = seed
        # ensure that subsequent scrolls don't mess up what swatches appear
        random.seed(seed)

        items = list(items)

        random.shuffle(items)
        data["title"] = "Library, sorted by Random"

    elif method == "color":
        items = sorted(items, key=get_hsv)
        data.update({"show_color_warning": True})
        data["title"] = "Library, sorted by Color"

    else:
        items = items.order_by("-date_published")

    # this loads the data obj with everything needed to render
    # the swatches
    data |= get_swatch_paginator(request, items)

    is_infinite = is_infinite_scroll_request(request)

    if is_infinite:
        # don't render the rest of the page, just the cards
        html = "partials/multiple_swatch_cards.partial"

    if is_searchbar_request(request):
        data |= {"is_searchbar_request": True}
        html = "partials/library_swatch_display.partial"

    # htmx needs to pass the existing filters along with the search
    # bar, so we have to provide it the filters to pass along
    params_minus_filter = {
        "m": method,
        "cf": color_family_str,
        "mfr": mfr_str,
        "ft": f_type_str,
        "td": td_range,
    }
    params_minus_filter = {
        k: v for k, v in params_minus_filter.items() if v is not None
    }

    # If there were swatches returned, then data["swatches"] will be a
    # Paginator object. If not, it'll be a QuerySet, so we need to check
    # for that.
    if hasattr(data["swatches"], "has_next"):
        if data["swatches"].has_next():
            params_plus_next_page = {
                **params_minus_filter,
                "p": data["requested_page"] + 1,
                "f": filter_str,
            }
            data.update({"infinite_scroll_params": json.dumps(params_plus_next_page)})

    if params_minus_filter:
        params_minus_filter = json.dumps(params_minus_filter)

    data.update(
        {
            "show_filter_bar": True,
            "active_filters": params_minus_filter,
        }
    )

    return prep_request(request, html, data)


def colorfamilysort(request: HttpRequest, family_id: str) -> HttpResponse:
    try:
        f_id = Swatch().get_color_id_from_slug_or_id(family_id)
    except UnknownSlugOrID:
        raise Http404

    family_name = [i[1] for i in Swatch.BASE_COLOR_OPTIONS if i[0] == f_id][0]

    data = build_data_dict(
        request,
        library=True,
        title=f"{family_name} Swatches",
        h1_title=f"{family_name} Swatches",
    )
    s = get_swatches(data)

    s = s.filter(Q(color_parent=f_id) | Q(alt_color_parent=f_id))

    return librarysort(request, library=s, prebuilt_data=data)


def manufacturersort(request: HttpRequest, mfr_id: str) -> HttpResponse:
    try:
        # it can either be the ID of the swatch itself or the slug
        mfr_id = int(mfr_id)
        args = {"id": mfr_id}
    except ValueError:
        args = {"slug": mfr_id}

    mfr = Manufacturer.objects.filter(**args).first()

    if not mfr:
        raise Http404

    data = build_data_dict(
        request,
        library=True,
        title=f"{mfr.name} Swatches",
        h1_title=f"{mfr.name} Swatches",
        show_unavailable_anyway=True,
    )
    s = get_swatches(data)

    s = s.filter(manufacturer=mfr)

    return librarysort(request, library=s, prebuilt_data=data)


def typesort(request: HttpRequest, f_type_id: int) -> HttpResponse:
    try:
        # it can either be the ID or the slug
        f_type_id = int(f_type_id)
        args = {"id": f_type_id}
    except ValueError:
        args = {"slug": f_type_id}

    f_type = GenericFilamentType.objects.filter(**args).first()

    if not f_type:
        raise Http404

    data = build_data_dict(
        request,
        library=True,
        title=f"{f_type.name} Swatches",
        h1_title=f"{f_type.name} Swatches",
    )

    s = get_swatches(data)

    s = s.filter(filament_type__parent_type=f_type)

    return librarysort(request, library=s, prebuilt_data=data)


def swatch_collection(request: HttpRequest, ids: str) -> HttpResponse:
    cleaned_ids = clean_collection_ids(ids)

    collection = Swatch.objects.filter(id__in=cleaned_ids, published=True)

    data = build_data_dict(
        request,
        library=True,
        collection_ids=",".join([str(i) for i in cleaned_ids]),
        show_collection_edit_button=True,
        title="Your Collection",
        h1_title="Your Collection",
    )

    return librarysort(request, library=collection, prebuilt_data=data)


def edit_swatch_collection(request: HttpRequest, ids: str) -> HttpResponse:
    cleaned_ids = clean_collection_ids(ids)
    data = build_data_dict(
        request,
        library=True,
        preselect_collection=cleaned_ids,
        title="Edit Collection",
    )
    library = get_swatches(data).order_by("-date_published")

    return librarysort(request, library=library, prebuilt_data=data)


#   _________ __                     .___      .__
#  /   _____//  |______    ____    __| _/____  |  |   ____   ____   ____
#  \_____  \\   __\__  \  /    \  / __ |\__  \ |  |  /  _ \ /    \_/ __ \
#  /        \|  |  / __ \|   |  \/ /_/ | / __ \|  |_(  <_> )   |  \  ___/
# /_______  /|__| (____  /___|  /\____ |(____  /____/\____/|___|  /\___  >
#         \/           \/     \/      \/     \/                 \/     \/


def swatch_detail(request: HttpRequest, swatch_id: str) -> HttpResponse:
    html = "standalone/swatch_detail.html"
    data = build_data_dict(request)
    try:
        # it can either be the ID of the swatch itself or the slug
        swatch_id = int(swatch_id)
        args = {"id": swatch_id}
    except ValueError:
        if swatch_id.lower().endswith("none"):
            # see #142 for context
            args = {"slug__startswith": swatch_id[:-4]}
        else:
            args = {"slug": swatch_id}

    # doing a simplified DB call allows reacting much faster when a filament
    # isn't found; this call is ~10x faster than the full call, and if the
    # is found, it's less than 1ms of penalty
    library = get_swatches(data, force_all=True)
    if not library.filter(**args).exists():
        raise Http404

    swatch = (
        library.filter(**args)
        .select_related(
            "complement",
            "complement__manufacturer",
            "complement__filament_type",
            "analogous_1",
            "analogous_1__manufacturer",
            "analogous_1__filament_type",
            "analogous_2",
            "analogous_2__filament_type",
            "analogous_2__manufacturer",
            "triadic_1",
            "triadic_1__filament_type",
            "triadic_1__manufacturer",
            "triadic_2",
            "triadic_2__filament_type",
            "triadic_2__manufacturer",
            "split_complement_1",
            "split_complement_1__filament_type",
            "split_complement_1__manufacturer",
            "split_complement_2",
            "split_complement_2__filament_type",
            "split_complement_2__manufacturer",
            "tetradic_1",
            "tetradic_1__filament_type",
            "tetradic_1__manufacturer",
            "tetradic_2",
            "tetradic_2__filament_type",
            "tetradic_2__manufacturer",
            "tetradic_3",
            "tetradic_3__filament_type",
            "tetradic_3__manufacturer",
            "square_1",
            "square_1__filament_type",
            "square_1__manufacturer",
            "square_2",
            "square_2__filament_type",
            "square_2__manufacturer",
            "square_3",
            "square_3__filament_type",
            "square_3__manufacturer",
            "closest_1",
            "closest_1__filament_type",
            "closest_1__manufacturer",
            "closest_2",
            "closest_2__filament_type",
            "closest_2__manufacturer",
            "closest_pantone_1",
            "closest_pantone_2",
            "closest_pantone_3",
            "closest_pms_1",
            "closest_pms_2",
            "closest_pms_3",
            "closest_ral_1",
            "closest_ral_2",
            "closest_ral_3",
            "closest_pms_1",
            "closest_pms_2",
            "closest_pms_3",
            "manufacturer",
            "filament_type",
        )
        .prefetch_related(
            "usersubmittedtd_set",
            "purchaselocation_set",
        )
    )

    swatch = swatch.first()

    if not swatch.published:
        raise Http404
    else:
        swatch.refresh_cache_if_needed()
        if generate_custom_library(data):
            swatch.update_all_color_matches(get_custom_library(data))

        data.update(
            {
                "swatch": swatch,
                "title": (
                    f"{swatch.manufacturer.name} - {swatch.color_name}"
                    f" {swatch.filament_type.name}"
                ),
            }
        )

        return prep_request(request, html, data)


def inventory_page(request: HttpRequest) -> HttpResponse:
    data = build_data_dict(request)
    data |= {
        "swatches": Swatch.objects.select_related("manufacturer")
        .prefetch_related("filament_type")
        .order_by(Lower("manufacturer__name"), Lower("color_name")),
        "title": "Inventory",
    }
    data |= {"published_count": data["swatches"].filter(published=True).count()}
    return prep_request(request, "standalone/inventory.html", data)


def report_bad_link(
    request: HttpRequest, swatch_id: int, link_type: str
) -> HttpResponse:
    try:
        swatch = Swatch.objects.get(id=swatch_id, published=True)
    except Swatch.DoesNotExist:
        raise Http404()

    current_link = request.POST.get("currentLink")

    if not current_link:
        messages.error(
            request,
            "Something went wrong with your request."
            " Please send me an email at joe@filamentcolors.xyz"
            " with the link you tried to report. Thanks!",
        )
        return HttpResponseRedirect(reverse("swatchdetail", args=[swatch_id]))

    DeadLink.objects.create(
        swatch=swatch,
        link_type=link_type,
        current_url=current_link,
        suggested_url=request.POST.get("newLink"),
    )

    messages.success(
        request,
        "Thanks! We've received your report.",
    )

    return HttpResponseRedirect(reverse("swatchdetail", args=[swatch_id]))


@csrf_exempt
def colormatch(request: HttpRequest) -> HttpResponse:
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
            if not matching_swatch:
                continue
            if data["user_settings"].get("show_delta_e_values"):
                distance = matching_swatch.get_distance_to(hex_to_rgb(incoming_color))
            else:
                distance = None

            matches.append([matching_swatch, distance])
            library = library.exclude(id=matching_swatch.id)

        data["colormatch_swatches"] = matches
        return prep_request(request, "partials/colormatch_results.partial", data)

    return prep_request(request, "standalone/colormatch.html", data)


def swatch_field_visualizer(request: HttpRequest) -> HttpResponse:
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


def manufacturer_list(request: HttpRequest) -> HttpResponse:
    return prep_request(
        request,
        "standalone/manufacturer_list.html",
        build_data_dict(request, title="Manufacturers"),
    )


def about_page(request: HttpRequest) -> HttpResponse:
    return prep_request(
        request, "standalone/about.html", build_data_dict(request, title="About")
    )


def monetary_donation_page(request: HttpRequest) -> HttpResponse:
    return prep_request(
        request,
        "standalone/monetary_donations.html",
        build_data_dict(request, title="Monetary Donations"),
    )


def about_me(request: HttpRequest) -> HttpResponse:
    return prep_request(
        request,
        "standalone/about_us.html",
        build_data_dict(request, title="About the Filament Librarian"),
    )


def donation_page(request: HttpRequest) -> HttpResponse:
    return prep_request(
        request,
        "standalone/donations.html",
        build_data_dict(request, title="Donations"),
    )


def error_400(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
    return prep_request(
        request,
        "400.html",
        build_data_dict(request, title="Something's not right..."),
        status=400,
    )


def error_404(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
    return prep_request(
        request,
        "404.html",
        build_data_dict(request, title="Can't find that..."),
        status=404,
    )


def error_500(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
    return prep_request(
        request,
        "500.html",
        build_data_dict(request, title="Something went wrong!"),
        status=500,
    )


# __________                __  .__       .__
# \______   \_____ ________/  |_|__|____  |  |   ______
#  |     ___/\__  \\_  __ \   __\  \__  \ |  |  /  ___/
#  |    |     / __ \|  | \/|  | |  |/ __ \|  |__\___ \
#  |____|    (____  /__|   |__| |__(____  /____/____  >
#                 \/                    \/          \/


def get_welcome_experience_image(request: HttpRequest, image_id: int) -> HttpResponse:
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


def get_welcome_experience_video(request: HttpRequest) -> HttpResponse:
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
