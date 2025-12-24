import colorsys
import json
import random
from typing import Any

import numpy
import pandas
from altcha import verify_solution
from colormath.color_conversions import convert_color
from colormath.color_objects import LabColor, sRGBColor
from django.conf import settings
from django.contrib import messages
from django.db.models import Q, QuerySet
from django.db.models.functions import Lower
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import HttpResponseRedirect, reverse
from django.views.decorators.csrf import csrf_exempt
from plotly import graph_objects

from filamentcolors import status
from filamentcolors.colors import convert_short_to_full_hex, is_hex, is_short_hex
from filamentcolors.exceptions import UnknownSlugOrID
from filamentcolors.helpers import (
    ErrorStatusResponse,
    apply_color_family_filter,
    apply_filament_parent_type_filter,
    apply_manufacturer_filter,
    apply_td_range_filter,
    build_data_dict,
    clean_collection_ids,
    filter_qs_by_search_string,
    generate_custom_library,
    get_custom_library,
    get_hsv,
    get_new_seed,
    get_swatch_paginator,
    get_swatches,
    is_infinite_scroll_request,
    is_searchbar_request,
    prep_request,
)
from filamentcolors.models import (
    DeadLink,
    GenericFilamentType,
    GenericFile,
    Manufacturer,
    Swatch,
)


def homepage(request: HttpRequest) -> HttpResponse:
    data = build_data_dict(request)
    data |= {
        "recent_swatches": Swatch.objects.filter(published=True).order_by(
            "-date_published"
        )[:9]
    }
    return prep_request(request, "standalone/landing.html", data)


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
        data.update({"search_prefill": filter_str})
        items = filter_qs_by_search_string(items, filter_str)

    # Shared filters via helpers
    items = apply_color_family_filter(items, color_family_str, strict=True)
    items = apply_manufacturer_filter(items, mfr_str, resolve=True, strict=True)
    items = apply_filament_parent_type_filter(items, f_type_str)
    items = apply_td_range_filter(items, td_range, treat_full_as_no_filter=True)

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
        # Default ordering must match API ordering to keep server-rendered
        # first page consistent with JSON pagination that follows. Add a
        # deterministic tie-breaker on id to avoid duplicates/gaps when
        # many items share the same publication timestamp (common in tests).
        items = items.order_by("-date_published", "-id")

    # this loads the data obj with everything needed to render
    # the swatches
    data |= get_swatch_paginator(request, items)

    if is_infinite_scroll_request(request):
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
    # If this is a manufacturer route, force the manufacturer slug into params
    forced_mfr = data.get("force_mfr_slug")
    if forced_mfr and not params_minus_filter.get("mfr"):
        params_minus_filter["mfr"] = forced_mfr

    # If this is a type route, force the parent type slug into params
    forced_ft = data.get("force_ft_slug")
    if forced_ft and not params_minus_filter.get("ft"):
        params_minus_filter["ft"] = forced_ft

    # If this is a color family route, force the color family identifier into params
    forced_cf = data.get("force_cf")
    if forced_cf and not params_minus_filter.get("cf"):
        params_minus_filter["cf"] = forced_cf

    # If we're rendering a Collection page, include the exact IDs so the
    # JSON paginator will constrain subsequent API requests to only these.
    collection_ids = data.get("collection_ids")
    if collection_ids:
        params_minus_filter["id__in"] = collection_ids

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
        else:
            data.update({settings.FC_NO_MORE: True})

    # NOTE: Do NOT JSON-dump params_minus_filter here.
    # The template uses `json_script` which will safely JSON-encode
    # this Python object into a JS value. If we pre-dump it, the
    # client receives a JSON string which then gets spread into
    # character-indexed query params like 0,1,2... in URLSearchParams.

    # For JSON pagination, include the search term in the active filters so the client
    # can continue paging with the same query across API requests.
    active_filters = dict(params_minus_filter)
    if filter_str:
        active_filters["f"] = filter_str

    data.update(
        {
            "show_filter_bar": True,
            "active_filters": active_filters,
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
    # Ensure client-side pagination keeps color family constraint
    # Pass through the original identifier (slug or id); API accepts either via `cf`
    data["force_cf"] = family_id
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
    # Ensure client-side pagination keeps manufacturer constraint
    data["force_mfr_slug"] = mfr.slug

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
    # Ensure client-side pagination keeps type constraint
    data["force_ft_slug"] = f_type.slug

    s = get_swatches(data)

    s = s.filter(filament_type__parent_type=f_type)

    return librarysort(request, library=s, prebuilt_data=data)


def swatch_collection(request: HttpRequest, ids: str) -> HttpResponse:
    cleaned_ids = clean_collection_ids(ids)
    # First, we need to identify if there are any swatches we need to go fishing for.
    relocated_swatches = Swatch.objects.filter(
        id__in=cleaned_ids, published=True, replaced_by__isnull=False
    )
    if relocated_swatches:
        for swatch in relocated_swatches:
            starter_id = swatch.id
            while True:
                if swatch.replaced_by:
                    swatch = swatch.replaced_by
                else:
                    break
            # Now we have the one we're supposed to link to
            if swatch.id not in cleaned_ids:
                # If it's not already here, add it in the same spot, then nuke the old
                # refence.
                cleaned_ids.insert(cleaned_ids.index(starter_id), swatch.id)
            cleaned_ids.remove(starter_id)

    # Now, refetch the collection with the updated ids
    collection = Swatch.objects.filter(id__in=cleaned_ids, published=True)

    # Because we modified the list of IDs if we had a replaced swatch, when we send
    # the updated list along with the button, the Edit button will transparently
    # work.
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
    collection_data = Swatch.objects.filter(id__in=cleaned_ids, published=True).values(
        "id", "color_name", "hex_color", "manufacturer__name", "filament_type__name"
    )

    for item in list(collection_data):
        # collapse down the data. This is a _massive_ data savings over the wire
        item["i"] = item.pop("id")
        item["n"] = item.pop("color_name")
        item["c"] = item.pop("hex_color")
        item["m"] = item.pop("manufacturer__name")
        item["t"] = item.pop("filament_type__name")

    data = build_data_dict(
        request,
        library=True,
        preselect_collection=cleaned_ids,
        preselect_data=list(collection_data),
        title="Edit Collection",
    )
    library = get_swatches(data).order_by("-date_published", "-id")

    return librarysort(request, library=library, prebuilt_data=data)


#   _________ __                     .___      .__
#  /   _____//  |______    ____    __| _/____  |  |   ____   ____   ____
#  \_____  \\   __\__  \  /    \  / __ |\__  \ |  |  /  _ \ /    \_/ __ \
#  /        \|  |  / __ \|   |  \/ /_/ | / __ \|  |_(  <_> )   |  \  ___/
# /_______  /|__| (____  /___|  /\____ |(____  /____/\____/|___|  /\___  >
#         \/           \/     \/      \/     \/                 \/     \/


def _get_swatch_args(swatch_id: str) -> dict[str, Any]:
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
    return args


def opengraph_card(request: HttpRequest, swatch_id: str) -> HttpResponse:
    html = "standalone/opengraph_card.html"
    data = build_data_dict(request)

    args = _get_swatch_args(swatch_id)

    args["published"] = True

    swatch = Swatch.objects.filter(**args).first()
    if not swatch:
        raise Http404
    data["obj"] = swatch
    return prep_request(request, html, data)


def swatch_detail(request: HttpRequest, swatch_id: str) -> HttpResponse:
    html = "standalone/swatch_detail.html"
    data = build_data_dict(request)
    args = _get_swatch_args(swatch_id)

    # doing a simplified DB call allows reacting much faster when a filament
    # isn't found; this call is ~10x faster than the full call, and if the
    # swatch is found, it's less than 1ms of penalty
    library = get_swatches(data, force_all=True)
    while True:
        if swatch := library.filter(**args).first():
            if not swatch.replaced_by:
                break
            args["id"] = swatch.replaced_by.id
        else:
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
        "swatches": Swatch.objects.filter(replaced_by__isnull=True)
        .select_related("manufacturer")
        .prefetch_related("filament_type")
        .order_by(Lower("manufacturer__name"), Lower("color_name")),
        "title": "Inventory",
    }
    return prep_request(request, "standalone/inventory.html", data)


def report_bad_link(
    request: HttpRequest, swatch_id: int, link_type: str
) -> HttpResponse:
    try:
        swatch = Swatch.objects.get(id=swatch_id, published=True)
    except Swatch.DoesNotExist:
        raise Http404()

    no_validation_error_text = "There was a problem with your request."
    validation_error_text = (
        "Validation failed; please try again."
        " If the problem persists, please send me an email at"
        " joe@filamentcolors.xyz. Thanks!"
    )
    generic_error_text = (
        "Something went wrong with your request."
        " Please send me an email at joe@filamentcolors.xyz"
        " with the link you tried to report. Thanks!"
    )

    swatch_redirect = HttpResponseRedirect(reverse("swatchdetail", args=[swatch_id]))

    altcha_payload = request.POST.get("altcha")
    if not altcha_payload:
        messages.error(request, no_validation_error_text)
        return swatch_redirect

    try:
        verified, err = verify_solution(altcha_payload, settings.ALTCHA_HMAC_KEY, True)
    except (TypeError, AttributeError):
        # Verification can explode if the payload is broken
        messages.error(request, validation_error_text)
        return swatch_redirect
    if not verified:
        messages.error(request, validation_error_text)
        return swatch_redirect

    match link_type:
        case "mfr":
            current_link = swatch.mfr_purchase_link
        case "amazon":
            current_link = swatch.amazon_purchase_link
        case _:
            messages.error(request, generic_error_text)
            return swatch_redirect

    DeadLink.objects.create(
        swatch=swatch,
        link_type=link_type,
        current_url=current_link,
        suggested_url=request.POST.get("newLink"),
    )

    messages.success(request, "Thanks! We've received your report.")

    return swatch_redirect


@csrf_exempt
def colormatch(request: HttpRequest) -> HttpResponse:
    data = build_data_dict(
        request,
        title="Color Match",
        show_colormatch_extras=True,
        show_delta_e_distance_warning=True,
    )

    if request.method == "POST":
        # Prefer LAB input if provided; fall back to HEX
        lab_l = request.POST.get("lab_l")
        lab_a = request.POST.get("lab_a")
        lab_b = request.POST.get("lab_b")

        target_lab = None  # LabColor used for distance and filtering
        if lab_l and lab_a and lab_b:
            try:
                l_val = float(str(lab_l).strip())
                a_val = float(str(lab_a).strip())
                b_val = float(str(lab_b).strip())
                # Clamp L to [0,100] like frontend does; A/B are typically within ~[-128,127]
                l_val = max(0.0, min(100.0, l_val))
                target_lab = LabColor(l_val, a_val, b_val)
            except (ValueError, TypeError):
                # If LAB provided but invalid, return bad color code
                return ErrorStatusResponse(status=status.HTTP_701_BAD_COLOR_CODE)
        else:
            incoming_color = request.POST.get("hex_color")
            if not incoming_color:
                # validation is always a good thing
                return ErrorStatusResponse(status=status.HTTP_702_MISSING_COLOR_CODE)
            if is_short_hex(incoming_color):
                incoming_color = convert_short_to_full_hex(incoming_color)
            if not is_hex(incoming_color):
                return ErrorStatusResponse(status=status.HTTP_701_BAD_COLOR_CODE)
            target_lab = convert_color(
                sRGBColor.new_from_rgb_hex(incoming_color), LabColor
            )

        library = get_swatches(data)
        matches = []

        for _ in range(data["user_settings"].get("number_of_colormatch_results", 3)):
            matching_swatch = Swatch().get_closest_color_swatch(library, target_lab)
            if not matching_swatch:
                continue
            distance = matching_swatch.get_distance_to(target_lab)
            matching_swatch.distance = distance
            matches.append(matching_swatch)
            library = library.exclude(id=matching_swatch.id)

        matches.sort(key=lambda s: s.distance)
        data["swatches"] = matches
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
        build_data_dict(request, title="About the Filament Librarians"),
    )


def donation_page(request: HttpRequest) -> HttpResponse:
    return prep_request(
        request,
        "standalone/donations.html",
        build_data_dict(request, title="Donations"),
    )


def work_with_us(request: HttpRequest) -> HttpResponse:
    return prep_request(
        request,
        "standalone/work_with_us.html",
        build_data_dict(request, title="Work With Us"),
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


def testpage(request):
    # show a page with random swatch card images for screenshots. Only works in dev mode
    data = build_data_dict(request)
    swatches = Swatch.objects.filter(published=True).order_by("?")[:100]
    data |= {"swatches": swatches}
    return prep_request(request, "standalone/testpage.html", data)


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


def inventory_search(request: HttpRequest) -> HttpResponse:
    if not request.htmx:
        return HttpResponse(status=404)

    value = request.GET.get("f", "")

    data = build_data_dict(request)

    data["results"] = filter_qs_by_search_string(Swatch.objects.all(), value)
    data["results_count"] = data["results"].count()
    data["minus_five"] = data["results_count"] - 5
    data["results"] = data["results"][:5]

    return prep_request(request, "htmx_partials/donation_sort_view.partial", data)
