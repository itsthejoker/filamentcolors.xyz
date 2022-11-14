import colorsys
from typing import Any, Dict, List

from django.db.models import Count, F, Q, QuerySet
from django.db.models.functions import Lower
from django.http import request, HttpResponse
from django.shortcuts import render

from filamentcolors.models import GenericFilamentType, GenericFile, Manufacturer, Swatch

have_visited_before_cookie = "f"
filament_type_settings_cookie = "show-types"
show_unavailable_cookie = "show-un"
mfr_blacklist_cookie = "mfr-blacklist"


def first_time_visitor(r: request) -> bool:
    return False if r.COOKIES.get(have_visited_before_cookie) else True


def prep_request(
        r: request, html: str, data: Dict = None, *args: Any, **kwargs: Any
) -> HttpResponse:
    """
    Prepare the actual request for serving.

    This allows checking every request for whether a visitor is new or not
    and returning the welcome modal if necessary without having to remember
    to write it into every view.
    """
    if not data:
        data = {}

    if first_time_visitor(r):
        data |= {"launch_welcome_modal": True}

    if r.htmx and not r.htmx.history_restore_request:
        data |= {"base_template": "partial_base.html"}
    else:
        data |= {
            "base_template": "base.html",
        }

    response = render(r, html, context=data, *args, **kwargs)
    response = set_tasty_cookies(response)

    return response


def get_hsv(item):
    # This seems to work but I don't know why or how
    hexrgb = item.hex_color
    r, g, b = (int(hexrgb[i: i + 2], 16) / 255.0 for i in range(0, 5, 2))
    return colorsys.rgb_to_hsv(r, g, b)


def set_tasty_cookies(response) -> HttpResponse:
    year = 365 * 24 * 60 * 60
    # Yet another chromium bug that goes unfixed. Don't enable `secure=True` or it
    # will break chrome testing locally.
    # https://bugs.chromium.org/p/chromium/issues/detail?id=757472
    response.set_cookie(
        have_visited_before_cookie, "tasty_cookies", max_age=year, samesite="lax"
    )
    return response


def build_data_dict(request, library: bool = False) -> Dict:
    """
    This request requires rendering the base template, so perform all
    the queries needed to populate it.
    Here's what these keys are used for:

      manufacturers               |   used to populate dropdown from navbar
      filament_types              |   ...
      color_family                |   ...
      welcome_experience_images   |   the urls for the example images shown in
                                  |       "how to use the site" modals.
      settings_buttons            |   model objects that power the settings page
      search_prefill              |   prepopulate the filter bar at top of page
      user_settings               |   a dict pulled from the user's browser
      is_library_view             |   a boolean; only show search bar on the library.
    :param request: Request
    :param library: bool
    :return: dict
    """
    return {
        "manufacturers": (
            Manufacturer.objects.exclude(
                id__in=(
                    Manufacturer.objects.annotate(
                        total_count=Count("swatch", distinct=True)
                    )
                    .filter(swatch__published=False)
                    .annotate(unpublished=Count("swatch", distinct=True))
                    .filter(Q(unpublished=F("total_count")))
                )
            )
            .exclude(id__in=Manufacturer.objects.filter(swatch__isnull=True))
            .order_by(Lower("name"))
            .annotate(
                swatch_count=Count("swatch", filter=Q(swatch__published=True))
            )
        ),
        "filament_types": GenericFilamentType.objects.order_by(Lower("name")),
        "color_family": Swatch.BASE_COLOR_OPTIONS,
        "welcome_experience_images": GenericFile.objects.filter(
            name__in=["step1", "step2", "step3", "step4"]
        ),
        "welcome_experience_movies": GenericFile.objects.filter(
            name__in=["collections_example", "collections_example_webm"]
        ),
        "settings_buttons": GenericFilamentType.objects.all(),
        "search_prefill": request.GET.get("q", ""),
        "user_settings": get_settings_cookies(request),
        "is_library_view": library,
    }


def clean_collection_ids(ids: str) -> List:
    # filter out bad input
    cleaned_ids = list()
    for item in ids.split(","):
        try:
            cleaned_ids.append(int(item))
        except ValueError:
            continue
    return cleaned_ids


def get_settings_cookies(r: request) -> Dict:
    # both of these cookies are set by the javascript in the frontend.
    type_settings = r.COOKIES.get(filament_type_settings_cookie)
    show_dc = r.COOKIES.get(show_unavailable_cookie)
    mfr_blacklist = r.COOKIES.get(mfr_blacklist_cookie)

    if type_settings:
        # It will be in this format: `1-true_2-true_3-true_6-false_9-false_`
        # The number is the ID for the GenericFilamentType (PLA, ABS, etc.)
        # the goal is to identify whether the user wants to see that particular
        # type in the library view and what types to exclude when doing a
        # modified color wheel search.
        type_settings = type_settings.split("_")
        if type_settings[-1] == "":
            type_settings.pop()

        types = [x.split("-")[0] for x in type_settings if x.split("-")[1] == "true"]
        types = GenericFilamentType.objects.filter(id__in=types)
    else:
        types = GenericFilamentType.objects.all()

    if mfr_blacklist:
        # in this format: 1-2-3-12-5-8-
        mfr_blacklist = mfr_blacklist.split("-")
        if mfr_blacklist[-1] == "":
            mfr_blacklist.pop()
        mfr_blacklist_objects = Manufacturer.objects.all().exclude(id__in=mfr_blacklist)
    else:
        mfr_blacklist_objects = Manufacturer.objects.all()

    return {
        "types": types,
        "show_unavailable": True if show_dc == "true" else False,
        "mfr_whitelist": mfr_blacklist_objects,
    }


def generate_custom_library(data: Dict) -> bool:
    """
    Return a boolean based on whether or not we actually need to generate
    our own queryset to do matching from. The data here is from the user's
    cookies that they send with the request, and their personal settings
    for the site may be different from the way we natively want to render
    it. The checks verify that nothing has changed, so we need to return
    the inverse of that (for example, false to show that we don't need to
    take any further action).

    :param data: Dict; the actual dict we'll use to build the templates.
    :return:
    """
    return not (
            len(data["user_settings"]["types"]) == GenericFilamentType.objects.count()
            and data["user_settings"]["show_unavailable"]
            and len(data["user_settings"]["mfr_whitelist"]) == Manufacturer.objects.count()
    )


def get_custom_library(data: Dict) -> QuerySet:
    s = (
        Swatch.objects.select_related("manufacturer")
        .prefetch_related("filament_type")
        .filter(filament_type__parent_type__in=data["user_settings"]["types"])
    )
    if data["user_settings"]["show_unavailable"] is False:
        s = s.exclude(amazon_purchase_link__isnull=True, mfr_purchase_link__isnull=True)

    return s.filter(
        manufacturer__in=data["user_settings"]["mfr_whitelist"], published=True
    )


def get_swatches(data: Dict) -> QuerySet:
    if generate_custom_library(data):
        queryset = get_custom_library(data)
    else:
        queryset = (
            Swatch.objects.select_related("manufacturer")
            .prefetch_related("filament_type")
            .filter(published=True)
        )
    return queryset
