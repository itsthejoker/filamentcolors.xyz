import colorsys

from filamentcolors.models import Swatch
from filamentcolors.colors import Color


def get_complement_swatch(s: Swatch) -> [None, Swatch]:
    """
    It's important to note that this will attempt to find the closest swatch
    in the library to the complement color. It is entirely possible that this
    will fail miserably and hilariously, because color is really, really hard.
    """
    complement = Color(s.hex_color).complementary()[1]

    distance_dict = dict()
    swatches = Swatch.objects.all()
    for item in swatches:
        possible_color = Color(item.hex_color)
        distance = complement.distance_to(possible_color)
        distance_dict.update({item: distance})

    distance_dict = {
        i:distance_dict[i] for i in distance_dict
        if distance_dict[i] is not None
    }

    sorted_distance_list = sorted(distance_dict.items(), key=lambda kv: kv[1])

    return sorted_distance_list[0][0]


def get_hsv(item):
    # TODO: I have NO idea if this works. Need to actually get some
    # samples up in here to check.

    # update: seems to work but I don't know why or how
    hexrgb = item.hex_color
    r, g, b = (int(hexrgb[i:i + 2], 16) / 255.0 for i in range(0, 5, 2))
    return colorsys.rgb_to_hsv(r, g, b)
