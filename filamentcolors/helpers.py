import colorsys

from django.db.models.functions import Lower
from django.http import request

from filamentcolors.models import Manufacturer
from filamentcolors.models import FilamentType

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
        'filament_types': FilamentType.objects.all().order_by(Lower('name'))
    }
