import colorsys
import secrets
from typing import Any, Dict, List

from django.conf import settings
from django.core.paginator import EmptyPage, Paginator
from django.db.models import (
    Case,
    Count,
    F,
    FloatField,
    OuterRef,
    Q,
    QuerySet,
    Subquery,
    Sum,
    Value,
    When,
)
from django.db.models.functions import Coalesce, Lower
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from filamentcolors import NAVBAR_MESSAGE, NAVBAR_MESSAGE_ID, NAVBAR_MESSAGE_ALLOW_DISMISSAL
from filamentcolors import status as status_codes
from filamentcolors.colors import clamp
from filamentcolors.models import (
    DeadLink,
    GenericFilamentType,
    Manufacturer,
    Swatch,
    UserSubmittedTD,
)

have_visited_before_cookie = "f"
filament_type_settings_cookie = "show-types"
show_unavailable_cookie = "show-un"
mfr_blacklist_cookie = "mfr-blacklist"
show_delta_e_values_cookie = "show-delta-e-values"
number_of_colormatch_results_cookie = "number-of-colormatch-results"


def first_time_visitor(r: HttpRequest) -> bool:
    return False if r.COOKIES.get(have_visited_before_cookie) else True


def prep_request(
    r: HttpRequest, html: str, data: Dict = None, *args: Any, **kwargs: Any
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

    # If we're returning a proper HTMX component, it will completely ignore
    # this template and just return the HTML we tell it to. If we're returning
    # a full page, we need to tell it which template to use.
    # TODO: There are a bunch of errors that say the htmx attribute doesn't
    #  exist. Figure out why. In the meantime, just do a check to see if the
    #  attribute is there, and if not, treat it like a full page load.
    if not hasattr(r, "htmx"):
        data |= {
            "base_template": "base.html",
        }
    else:
        if r.htmx and not r.htmx.history_restore_request:
            data |= {"base_template": "partial_base.html"}
        else:
            data |= {
                "base_template": "base.html",
            }
    if status := data.get("status_code"):
        kwargs.update({"status": status})
    response = render(r, html, context=data, *args, **kwargs)
    response = set_tasty_cookies(response)

    return response


def get_hsv(item):
    # This seems to work but I don't know why or how
    hexrgb = item.hex_color
    r, g, b = (int(hexrgb[i : i + 2], 16) / 255.0 for i in range(0, 5, 2))
    return colorsys.rgb_to_hsv(r, g, b)


def set_tasty_cookies(response) -> HttpResponse:
    year = 365 * 24 * 60 * 60
    # Yet another chromium bug that goes unfixed. Don't enable `secure=True` or it
    # will break chrome testing locally.
    # https://bugs.chromium.org/p/chromium/issues/detail?id=757472
    response.set_cookie(
        have_visited_before_cookie,
        "tasty_cookies",
        max_age=year,
        samesite="lax",
        secure=True,
    )
    return response


def build_data_dict(
    request: HttpRequest, library: bool = False, title: str = None, **kwargs
) -> Dict:
    """
    This request requires rendering the base template, so perform all
    the queries needed to populate it.
    Here's what these keys are used for:

      manufacturers                  |   used to populate dropdown from navbar
      filament_types                 |   ...
      color_family                   |   ...
      settings_buttons               |   model objects that power the settings page
      search_prefill                 |   prepopulate the filter bar at top of page
      user_settings                  |   a dict pulled from the user's browser
      show_search_bar                |   a boolean or boolean-like; only show search
                                     |     bar on the library.
      title                          |   the title of the page in the browser
      navbar_message                 |   the text of an optional banner message
                                     |     or announcement at the top of the site.
      navbar_message_id              |   the ID of that particular message. Each
                                     |     message can be dismissed separately, so
                                     |     each one having its own ID is important.
      navbar_message_allow_dismissal |   whether the banner message can be dismissed.
      browser_console_message        |   for debugging. Pass a string in here to have
                                     |     it written as a JS console log in the browser.
      browser_console_message2       |   ...
      browser_console_message3       |   ...

    :param request: WSGIRequest
    :param library: bool
    :param title: str
    :return: dict
    """
    user_settings = get_settings_cookies(request)
    data = {
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
                available_swatch_count=Count(
                    "swatch",
                    filter=Q(swatch__published=True, swatch__replaced_by__isnull=True)
                    & Q(
                        Q(swatch__amazon_purchase_link__isnull=False)
                        | Q(swatch__mfr_purchase_link__isnull=False)
                    ),
                )
            )
            .annotate(
                unavailable_swatch_count=Count(
                    "swatch",
                    filter=Q(swatch__published=True, swatch__replaced_by__isnull=True)
                    & Q(swatch__amazon_purchase_link__isnull=True)
                    & Q(swatch__mfr_purchase_link__isnull=True),
                )
            )
        ),
        "filament_types": GenericFilamentType.objects.order_by(Lower("name")),
        "color_family": Swatch.BASE_COLOR_OPTIONS,
        "settings_buttons": GenericFilamentType.objects.all(),
        "search_prefill": request.GET.get("q", ""),
        "user_settings": user_settings,
        "show_search_bar": library,
        "title": title or "FilamentColors",
        "navbar_message": NAVBAR_MESSAGE,
        "navbar_message_id": NAVBAR_MESSAGE_ID,
        "navbar_message_allow_dismissal": NAVBAR_MESSAGE_ALLOW_DISMISSAL,
        "browser_console_message": "",
        "browser_console_message2": "",
        "browser_console_message3": "",
    }
    if data.get("navbar_message_id") in user_settings.get("hide_alert_ids"):
        # they've manually dismissed it, so remove the message. If we change the message
        # (and the corresponding ID) then it will display until they click the close
        # button again.
        del data["navbar_message"]

    if hasattr(request, "user"):
        if request.user.is_staff:
            data["deadlink_count"] = DeadLink.objects.count()

    data.update(**kwargs)

    return data


def clean_collection_ids(ids: str) -> List:
    # filter out bad input
    cleaned_ids = list()
    for item in ids.split(","):
        try:
            cleaned_ids.append(int(item))
        except ValueError:
            continue
    return cleaned_ids


def debug_check_for_cookies(r: HttpRequest):
    type_settings = r.COOKIES.get(filament_type_settings_cookie)
    show_dc = r.COOKIES.get(show_unavailable_cookie)
    mfr_blacklist = r.COOKIES.get(mfr_blacklist_cookie)

    message = "Missing: "
    objs = []
    if not type_settings:
        objs.append("type_settings")
    if not show_dc:
        objs.append("show_dc")
    if not mfr_blacklist:
        objs.append("mfr_blacklist")
    if not objs:
        message = "all cookies accounted for"
    else:
        message = message + ", ".join(objs)
    return message


def get_settings_cookies(r: HttpRequest) -> Dict:
    # both of these cookies are set by the javascript in the frontend.
    default_colormatch_count = 4
    navbar_alert_key = "hideNavbarAlert-"
    type_settings = r.COOKIES.get(filament_type_settings_cookie)
    show_dc = r.COOKIES.get(show_unavailable_cookie)
    mfr_blacklist = r.COOKIES.get(mfr_blacklist_cookie)
    show_delta_e_values = r.COOKIES.get(show_delta_e_values_cookie)
    number_of_colormatch_results = r.COOKIES.get(
        number_of_colormatch_results_cookie, default_colormatch_count
    )
    hide_alert_ids = [
        i[len(navbar_alert_key) :]
        for i in r.COOKIES.keys()
        if i.startswith(navbar_alert_key)
    ]

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

    if number_of_colormatch_results:
        try:
            number_of_colormatch_results = int(number_of_colormatch_results)
            number_of_colormatch_results = clamp(
                number_of_colormatch_results, 3, 12
            )
        except ValueError:
            number_of_colormatch_results = default_colormatch_count
    else:
        number_of_colormatch_results = default_colormatch_count

    return {
        "types": types,
        "show_unavailable": True if show_dc == "true" else False,
        "mfr_whitelist": mfr_blacklist_objects,
        "show_delta_e_values": True if show_delta_e_values == "true" else False,
        "hide_alert_ids": hide_alert_ids,
        "number_of_colormatch_results": number_of_colormatch_results,
    }


def annotate_with_calculated_td(qs: QuerySet) -> QuerySet:
    """Handles the subquery math required to take an unknown number of
    user-submitted TDs and properly calculate the TD values.
    """
    user_tds_sum = (
        UserSubmittedTD.objects.filter(swatch=OuterRef("pk"))
        .values("swatch")
        .annotate(sum_td=Sum("td"))
        .values("sum_td")
    )
    user_tds_count = (
        UserSubmittedTD.objects.filter(swatch=OuterRef("pk"))
        .values("swatch")
        .annotate(count_td=Count("td"))
        .values("count_td")
    )

    return qs.annotate(
        user_tds_sum=Coalesce(
            Subquery(user_tds_sum, output_field=FloatField()),
            Value(0),
            output_field=FloatField(),
        ),
        user_tds_count=Coalesce(
            Subquery(user_tds_count, output_field=FloatField()),
            Value(0),
            output_field=FloatField(),
        ),
    ).annotate(
        calculated_td=Case(
            When(user_tds_count=0, then=F("td")),
            default=(F("td") + F("user_tds_sum")) / (1 + F("user_tds_count")),
            output_field=FloatField(),
        )
    )


def generate_custom_library(data: Dict) -> bool:
    """
    Return a boolean based on whether we actually need to generate
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
        Swatch.objects.filter(
            filament_type__parent_type__in=data["user_settings"]["types"],
            replaced_by__isnull=True
        )
        .select_related("manufacturer")
        .prefetch_related("filament_type")
    )
    if data["user_settings"]["show_unavailable"] is False and not data.get(
        "show_unavailable_anyway"
    ):
        s = s.exclude(amazon_purchase_link__isnull=True, mfr_purchase_link__isnull=True)

    return s.filter(
        manufacturer__in=data["user_settings"]["mfr_whitelist"], published=True
    )


def get_swatches(data: Dict, force_all: bool = False) -> QuerySet:
    # `force_all` is for when we want a swatch to be findable even if the user's
    # settings would normally exclude it. An example is for the swatch detail
    # page, where we want to load the swatch as long as it's published. What if
    # they get sent a link to a filament they've disabled the type for? The page
    # should still load, yanno.
    if generate_custom_library(data) and not force_all:
        queryset = get_custom_library(data)
    else:
        queryset = (
            Swatch.objects.filter(published=True)
            .select_related("manufacturer")
            .prefetch_related("filament_type")
        )
    queryset = annotate_with_calculated_td(queryset)
    return queryset


class ErrorStatusResponse(HttpResponse):
    def __init__(self, status: int = None) -> None:
        super().__init__()
        self.status_code = status
        self._reason_phrase = status_codes.reasons.get(status, "Unknown Status Code")


def is_infinite_scroll_request(request: HttpRequest) -> bool:
    return bool(request.headers.get("X-Infinite-Scroll", False))


def is_searchbar_request(request: HttpRequest) -> bool:
    return bool(request.headers.get("X-Searchbar", False))


def get_swatch_paginator(
    request: HttpRequest, items: QuerySet[Swatch]
) -> Dict[str, Any]:
    paginator_data = {}
    paginator = Paginator(items, settings.PAGINATION_COUNT)
    paginator_data.update({"paginator": paginator})
    requested_page = request.GET.get("p", None)
    requested_page = get_paginator_page(requested_page, 1)
    is_infinite = is_infinite_scroll_request(request)

    if is_infinite:
        # don't render the rest of the page, just the cards
        paginator_data |= {"html": "partials/multiple_swatch_cards.partial"}

    if requested_page > 1 and not is_infinite:
        # When a page is requested specifically by the browser, include
        # previous pages. Normal routing will not need the previous pages
        # because they'll already be there.
        paginator_data |= {
            "previous_pages_to_render": [
                paginator.page(i) for i in range(1, requested_page)
            ]
        }
    try:
        page = paginator.page(requested_page)
    except EmptyPage:
        page = Swatch.objects.none()

    paginator_data.update({"swatches": page, "requested_page": requested_page})
    return paginator_data


def get_paginator_page(potential_page: Any, value_if_invalid: int) -> int:
    if not potential_page:
        return value_if_invalid
    else:
        try:
            return max(int(potential_page), 1)
        except ValueError:
            return value_if_invalid


def get_new_seed() -> int:
    # since we're screwing with the seed for the python `random` module,
    # we need a cryptographically secure way to generate a new seed.
    # This uses the underlying OS to generate a random number.
    return secrets.SystemRandom().getrandbits(64)
