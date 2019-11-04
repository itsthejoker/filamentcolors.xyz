import colorsys
from typing import List

from django.db.models.functions import Lower
from django.http import request

from filamentcolors.models import Manufacturer
from filamentcolors.models import GenericFilamentType
from filamentcolors.models import Swatch
from filamentcolors.models import GenericFile


cookie_name = "f"


def show_welcome_modal(r: request):
    return False if r.COOKIES.get(cookie_name) else True


def get_hsv(item):
    # TODO: I have NO idea if this works. Need to actually get some
    # samples up in here to check.

    # update: seems to work but I don't know why or how
    hexrgb = item.hex_color
    r, g, b = (int(hexrgb[i:i + 2], 16) / 255.0 for i in range(0, 5, 2))
    return colorsys.rgb_to_hsv(r, g, b)


def set_tasty_cookies(response):
    year = 365 * 24 * 60 * 60
    response.set_cookie(cookie_name, 'tasty_cookies', max_age=year)


def build_data_dict(request):
    return {
        'search_prefill': request.GET.get('q', ''),
        'manufacturers': Manufacturer.objects.all().order_by(Lower('name')),
        'filament_types': GenericFilamentType.objects.all().order_by(Lower('name')),
        'color_family': Swatch.BASE_COLOR_OPTIONS,
        'welcome_experience_images': [
            GenericFile.objects.filter(file__startswith=X).first() for X in [
                'step1', 'step2', 'step3', 'step4'
            ]
        ]
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
