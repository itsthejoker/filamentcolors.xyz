import colorsys
from typing import List, Dict

from django.db.models.functions import Lower
from django.db.models.query import QuerySet
from django.db.models import Q
from django.http import request

from filamentcolors.models import GenericFilamentType
from filamentcolors.models import GenericFile
from filamentcolors.models import Manufacturer
from filamentcolors.models import Swatch

have_visited_before_cookie = "f"
filament_type_settings_cookie = "show-types"
show_unavailable_cookie = "show-un"
mfr_whitelist_cookie = "mfr-whitelist"


def show_welcome_modal(r: request):
    return False if r.COOKIES.get(have_visited_before_cookie) else True


def get_hsv(item):
    # TODO: I have NO idea if this works. Need to actually get some
    # samples up in here to check.

    # update: seems to work but I don't know why or how
    hexrgb = item.hex_color
    r, g, b = (int(hexrgb[i:i + 2], 16) / 255.0 for i in range(0, 5, 2))
    return colorsys.rgb_to_hsv(r, g, b)


def set_tasty_cookies(response):
    year = 365 * 24 * 60 * 60
    response.set_cookie(have_visited_before_cookie, 'tasty_cookies', max_age=year)


def build_data_dict(request):
    cookie_data = get_settings_cookies(request)

    return {
        'search_prefill': request.GET.get('q', ''),
        'manufacturers': Manufacturer.objects.all().order_by(Lower('name')),
        'filament_types': GenericFilamentType.objects.all().order_by(Lower('name')),
        'color_family': Swatch.BASE_COLOR_OPTIONS,
        'welcome_experience_images': [
            GenericFile.objects.filter(file__startswith=X).first() for X in [
                'step1', 'step2', 'step3', 'step4'
            ]
        ],
        'settings_buttons': GenericFilamentType.objects.all(),
        'user_settings': get_settings_cookies(request),
    }


def clean_collection_ids(ids: str) -> List:
    # filter out bad input
    cleaned_ids = list()
    for item in ids.split(','):
        try:
            cleaned_ids.append(int(item))
        except ValueError:
            continue
    return cleaned_ids


def get_settings_cookies(r: request) -> Dict:
    # both of these cookies are set by the javascript in the frontend.
    type_settings = r.COOKIES.get(filament_type_settings_cookie)
    show_dc = r.COOKIES.get(show_unavailable_cookie)
    mfr_whitelist = r.COOKIES.get(mfr_whitelist_cookie)

    if type_settings:
        # It will be in this format: `1-true_2-true_3-true_6-false_9-false_`
        # The number is the ID for the GenericFilamentType (PLA, ABS, etc.)
        # the goal is to identify whether the user wants to see that particular
        # type in the library view and what types to exclude when doing a
        # modified color wheel search.
        type_settings = type_settings.split('_')
        if type_settings[-1] == '':
            type_settings.pop()

        types = [
            GenericFilamentType.objects.get(id=x.split('-')[0])
            for x in type_settings
            if x.split('-')[1] == 'true'
        ]
    else:
        types = GenericFilamentType.objects.all()

    if mfr_whitelist:
        # in this format: 1-2-3-12-5-8-
        mfr_whitelist = mfr_whitelist.split('-')
        if mfr_whitelist[-1] == '':
            mfr_whitelist.pop()
        mfr_whitelist = [
            Manufacturer.objects.get(id=x) for x in mfr_whitelist
        ]
    else:
        mfr_whitelist = Manufacturer.objects.all()

    return {
        'types': types,
        'show_unavailable': True if show_dc == "true" else False,
        'mfr_whitelist': mfr_whitelist
    }


def generate_custom_library(data: Dict):
    """
    Return a boolean based on whether or not we actually need to generate
    our own queryset to do matching from. The checks verify that nothing has
    changed, so we need to return the inverse of that (for example, false
    to show that we don't need to take any further action).

    :param data: Dict; the actual dict we'll use to build the templates.
    :return:
    """
    return not (
            len(data['user_settings']['types']) ==
            GenericFilamentType.objects.count() and
            data['user_settings']['show_unavailable'] and
            len(data['user_settings']['mfr_whitelist']) ==
            Manufacturer.objects.count()
    )


def get_custom_library(data: Dict) -> QuerySet:
    s = Swatch.objects.filter(
        filament_type__parent_type__in=data['user_settings']['types']
    )
    if data['user_settings']['show_unavailable'] is False:
        s = s.filter(~Q(tags__name="unavailable"))

    s = s.filter(manufacturer__in=data['user_settings']['mfr_whitelist'])

    return s


def get_swatches(data: Dict) -> QuerySet:
    if generate_custom_library(data):
        s = get_custom_library(data)
    else:
        s = Swatch.objects.all()
    return s
