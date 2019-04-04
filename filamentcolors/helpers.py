import colorsys

from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cmc
from colormath.color_objects import LabColor
from colormath.color_objects import sRGBColor
from django.db.models.functions import Lower
from django.http import request

from filamentcolors.colors import Color
from filamentcolors.models import Manufacturer
from filamentcolors.models import Swatch

cookie_name = "f"


def show_welcome_modal(r: request):
    return False if r.COOKIES.get(cookie_name) else True


def get_complement_swatch(s: Swatch) -> [None, Swatch]:
    """
    It's important to note that this will attempt to find the closest swatch
    in the library to the complement color. It is entirely possible that this
    will fail miserably and hilariously, because color is really, really hard.
    """
    complement = Color(s.hex_color).complementary()[1]
    complement = convert_color(
        sRGBColor.new_from_rgb_hex(str(complement)), LabColor
    )

    distance_dict = dict()
    swatches = Swatch.objects.all()
    for item in swatches:
        possible_color = convert_color(
            sRGBColor.new_from_rgb_hex(item.hex_color), LabColor
        )

        distance = delta_e_cmc(complement, possible_color)

        distance_dict.update({item: distance})

    distance_dict = {
        i: distance_dict[i] for i in distance_dict
        if distance_dict[i] is not None
    }

    sorted_distance_list = sorted(distance_dict.items(), key=lambda kv: kv[1])

    try:
        return sorted_distance_list[0][0]
    except IndexError:
        return None


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
        'manufacturers': Manufacturer.objects.all().order_by(Lower('name'))
    }
