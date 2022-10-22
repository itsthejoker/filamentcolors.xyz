#!/usr/bin/env python3


# This script deals with color conversions and color transformations.
#
# copyright (C) 2014-2017  Martin Engqvist | martin_engqvist@hotmail.com
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# LICENSE:
#
# colcol is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# colcol is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#

# I have added several formatting and functional modifications to this
# file to make it better suit my requirements. @itsthejoker, 2019/1/10

__version__ = "0.13.0"

import colorsys
import math
import re
from typing import List, Tuple, Union

import numpy


def ColorDistance(rgb1: Union[Tuple, List], rgb2: Union[Tuple, List]) -> float:
    """
    This function calculates and returns the relative distance between two
    RGB colors. It's up for debate how accurate or useful this is, but it's
    better than nothing and also I have no idea what I'm doing. It's worth
    noting that this is Euclidean distance, which uses the true value of the
    colors and is only barely better than nothing when it comes to actually
    comparing two colors.
    See https://stackoverflow.com/a/14097641 for the origin of this
    function and also some more explanations of exactly what's going on and why
    this is probably a bad idea. More info: https://www.compuphase.com/cmetric.htm

    :param rgb1: Tuple or list; the first RGB color to compare.
    :param rgb2: Tuple or list; the second RGB color to compare.
    :return: float; the distance between the first color and the second.
             Approximately.
    """
    rgb1 = numpy.array(rgb1)
    rgb2 = numpy.array(rgb2)

    rm = 0.5 * (rgb1[0] + rgb2[0])
    distance = math.sqrt(sum((2 + rm, 4, 3 - rm) * (rgb1 - rgb2) ** 2))

    return distance


def is_rgb(in_col):
    """
    Check whether input is a valid RGB color.
    Return True if it is, otherwise False.
    """
    if len(in_col) == 3 and type(in_col) == tuple:
        if (
            type(in_col[0]) is int
            and type(in_col[1])
            and type(in_col[2])
            and 0 <= in_col[0] <= 255
            and 0 <= in_col[1] <= 255
            and 0 <= in_col[2] <= 255
        ):
            return True
        else:
            return False
    else:
        return False


def is_hex(in_col):
    """
    Check whether an input string is a valid hex value.
    Return True if it is, otherwise False.
    """
    if type(in_col) is not str:
        return False

    regular_expression = re.compile(
        r"""^  # match beginning of string
        [#]?  # exactly one hash, but optional
        [0-9a-fA-F]{6}  # exactly six of the hex symbols 0 to 9, a to f
        $  # match end of string
        """,
        re.VERBOSE | re.MULTILINE,
    )

    if regular_expression.match(in_col) == None:
        return False
    else:
        return True


def is_hsl(in_col):
    """
    Check whether an input is a valid HSL color.
    Return True if it is, otherwise False.
    """
    if len(in_col) == 3 and type(in_col) == tuple:
        if 0 <= in_col[0] <= 1 and 0 <= in_col[1] <= 1 and 0 <= in_col[2] <= 1:
            return True
        else:
            return False
    else:
        return False


def rgb_to_hex(rgb):
    """
    Convert RGB colors to hex.
    Input should be a tuple of integers (R, G, B) where each is between 0 and 255.
    Output is a string representing a hex number. For instance '#FFFFFF'.
    """
    # make sure input is ok
    assert is_rgb(rgb) is True, "Error, %s is not a valid RGB color." % rgb

    # make conversion
    return "#%02x%02x%02x".lower() % rgb


def hex_to_rgb(in_col):
    """
    Convert a hex color to RGB.
    Input should be a string. For example '#FFFFFF'.
    Output is a tuple of integers (R, G, B).
    """
    # make sure input is ok
    assert is_hex(in_col) is True, f"Error, {in_col} is not a valid hex color."

    # make the conversion
    in_col = in_col.lstrip("#")
    return tuple([int(in_col[s : s + 2], 16) for s in range(0, len(in_col), 2)])


def rgb_to_hsl(in_col):
    """
    Convert RGB colors to HSL.
    Input should be a tuple of integers (R, G, B) where each is between 0 and
    255. Output is a tuple of floats between 0.0 and 1.0.
    """
    assert is_rgb(in_col), "Error, %s is not a valid RGB color." % in_col

    # Convert each RGB integer to a float between 0 and 1
    r, g, b = [x / 255.0 for x in in_col]

    # RGB -> HSL
    h, l, s = colorsys.rgb_to_hls(r, g, b)

    return (h, s, l)


def hsl_to_rgb(in_col):
    """
    Convert HSL colors to RGB.
    Input should be a tuple of floats between 0.0 and 1.0.
    Output is a tuple of integers (R, G, B) where each is between 0 and 255.
    """
    assert is_hsl(in_col), f"Error, {str(in_col)} is not a valid HSL color."

    # assign to variables
    h, s, l = in_col

    # RGB -> HSL
    r, g, b = colorsys.hls_to_rgb(h, l, s)

    # convert it back to the appropriate integers
    r = int(round(255 * r))
    g = int(round(255 * g))
    b = int(round(255 * b))

    return (r, g, b)


def hex_to_hsl(in_col):
    """
    Convert a hex color to hsl.
    Input should be a string. For example '#FFFFFF'.
    Output is a tuple of ...... . For instance: (h, s, l).
    """
    return rgb_to_hsl(hex_to_rgb(in_col))


def hsl_to_hex(in_col):
    """
    Convert hsl color to hex.

    """
    return rgb_to_hex(hsl_to_rgb(in_col))


class Color:
    """
    A color class
    """

    def __init__(self, in_col):
        self.colors = {
            "aliceblue": "#F0F8FF",
            "antiquewhite": "#FAEBD7",
            "aqua": "#00FFFF",
            "aquamarine": "#7FFFD4",
            "azure": "#F0FFFF",
            "beige": "#F5F5DC",
            "bisque": "#FFE4C4",
            "black": "#000000",
            "blanchedalmond": "#FFEBCD",
            "blue": "#0000FF",
            "blueviolet": "#8A2BE2",
            "brown": "#A52A2A",
            "burlywood": "#DEB887",
            "cadetblue": "#5F9EA0",
            "chartreuse": "#7FFF00",
            "chocolate": "#D2691E",
            "coral": "#FF7F50",
            "cornflowerblue": "#6495ED",
            "cornsilk": "#FFF8DC",
            "crimson": "#DC143C",
            "cyan": "#00FFFF",
            "darkblue": "#00008B",
            "darkcyan": "#008B8B",
            "darkgoldenrod": "#B8860B",
            "darkgrey": "#A9A9A9",
            "darkgreen": "#006400",
            "darkkhaki": "#BDB76B",
            "darkmagenta": "#8B008B",
            "darkolivegreen": "#556B2F",
            "darkorange": "#FF8C00",
            "darkorchid": "#9932CC",
            "darkred": "#8B0000",
            "darksalmon": "#E9967A",
            "darkseagreen": "#8FBC8F",
            "darkslateblue": "#483D8B",
            "darkslategrey": "#2F4F4F",
            "darkturquoise": "#00CED1",
            "darkviolet": "#9400D3",
            "deeppink": "#FF1493",
            "deepskyblue": "#00BFFF",
            "dimgray": "#696969",
            "dimgrey": "#696969",
            "dodgerblue": "#1E90FF",
            "firebrick": "#B22222",
            "floralwhite": "#FFFAF0",
            "forestgreen": "#228B22",
            "fuchsia": "#FF00FF",
            "gainsboro": "#DCDCDC",
            "ghostwhite": "#F8F8FF",
            "gold": "#FFD700",
            "goldenrod": "#DAA520",
            "gray": "#808080",
            "grey": "#808080",
            "green": "#008000",
            "greenyellow": "#ADFF2F",
            "honeydew": "#F0FFF0",
            "hotpink": "#FF69B4",
            "indianred": "#CD5C5C",
            "indigo": "#4B0082",
            "ivory": "#FFFFF0",
            "khaki": "#F0E68C",
            "lavender": "#E6E6FA",
            "lavenderblush": "#FFF0F5",
            "lawngreen": "#7CFC00",
            "lemonchiffon": "#FFFACD",
            "lightblue": "#ADD8E6",
            "lightcoral": "#F08080",
            "lightcyan": "#E0FFFF",
            "lightgoldenrodyellow": "#FAFAD2",
            "lightgrey": "#D3D3D3",
            "lightgreen": "#90EE90",
            "lightpink": "#FFB6C1",
            "lightsalmon": "#FFA07A",
            "lightseagreen": "#20B2AA",
            "lightskyblue": "#87CEFA",
            "lightslategrey": "#778899",
            "lightsteelblue": "#B0C4DE",
            "lightyellow": "#FFFFE0",
            "lime": "#00FF00",
            "limegreen": "#32CD32",
            "linen": "#FAF0E6",
            "magenta": "#FF00FF",
            "maroon": "#800000",
            "mediumaquamarine": "#66CDAA",
            "mediumblue": "#0000CD",
            "mediumorchid": "#BA55D3",
            "mediumpurple": "#9370DB",
            "mediumseagreen": "#3CB371",
            "mediumslateblue": "#7B68EE",
            "mediumspringgreen": "#00FA9A",
            "mediumturquoise": "#48D1CC",
            "mediumvioletred": "#C71585",
            "midnightblue": "#191970",
            "mintcream": "#F5FFFA",
            "mistyrose": "#FFE4E1",
            "moccasin": "#FFE4B5",
            "navajowhite": "#FFDEAD",
            "navy": "#000080",
            "oldlace": "#FDF5E6",
            "olive": "#808000",
            "olivedrab": "#6B8E23",
            "orange": "#FFA500",
            "orangered": "#FF4500",
            "orchid": "#DA70D6",
            "palegoldenrod": "#EEE8AA",
            "palegreen": "#98FB98",
            "paleturquoise": "#AFEEEE",
            "palevioletred": "#DB7093",
            "papayawhip": "#FFEFD5",
            "peachpuff": "#FFDAB9",
            "peru": "#CD853F",
            "pink": "#FFC0CB",
            "plum": "#DDA0DD",
            "powderblue": "#B0E0E6",
            "purple": "#800080",
            "rebeccapurple": "#663399",
            "red": "#FF0000",
            "rosybrown": "#BC8F8F",
            "royalblue": "#4169E1",
            "saddlebrown": "#8B4513",
            "salmon": "#FA8072",
            "sandybrown": "#F4A460",
            "seagreen": "#2E8B57",
            "seashell": "#FFF5EE",
            "sienna": "#A0522D",
            "silver": "#C0C0C0",
            "skyblue": "#87CEEB",
            "slateblue": "#6A5ACD",
            "slategrey": "#708090",
            "snow": "#FFFAFA",
            "springgreen": "#00FF7F",
            "steelblue": "#4682B4",
            "tan": "#D2B48C",
            "teal": "#008080",
            "thistle": "#D8BFD8",
            "tomato": "#FF6347",
            "turquoise": "#40E0D0",
            "violet": "#EE82EE",
            "wheat": "#F5DEB3",
            "white": "#FFFFFF",
            "whitesmoke": "#F5F5F5",
            "yellow": "#FFFF00",
            "yellowgreen": "#9ACD32",
        }

        # make sure the input color is valid
        assert (
            is_rgb(in_col) or is_hex(in_col) or in_col.lower() in self.colors.keys()
        ), (
            f'Error, the input color "{in_col}" is not a valid rgb color, hex '
            f"color or named color"
        )

        if (
            is_rgb(in_col) is False
            and is_hex(in_col) is False
            and in_col.lower() in self.colors.keys()
        ):
            in_col = self.colors[in_col.lower()]

        # set variables
        self._set_color(in_col)

    def __str__(self):
        """
        Change how object prints.
        """
        if self.get_format() == "hex":
            return str(rgb_to_hex(self.col))
        else:
            return str(self.col)

    def __repr__(self):
        """
        Change how object is represented.
        """
        return self.__str__()

    def __eq__(self, other):
        """Override the default Equals behavior"""
        if isinstance(other, self.__class__):
            if self.get_format() == "hex":
                return str(rgb_to_hex(self.col)) == other.__str__()
            else:
                return self.col == other.__str__()

        else:
            if self.get_format() == "hex":
                return str(rgb_to_hex(self.col)) == other
            else:
                return self.col == other

    def distance_to(self, color) -> [float, None]:
        """
        Convenience function for ColorDistance().

        Pass in another instance of a color and this will return the relative
        distance between this color and the second. Or None if it can't be
        computed, which happens sometimes when one of the colors is close to
        black. I don't really know why.
        """
        error_state = None

        if not isinstance(color, Color):
            raise ValueError("Must compare instances of Color!")

        try:
            distance = ColorDistance(self.rgb(), color.rgb())
        except (ValueError, RuntimeWarning):  # math or numpy pitching a fit
            return error_state

        if distance == "nan":
            return error_state

        return distance

    def _set_color(self, in_col):
        """
        Private method to set the color variables.
        """
        # check whether input is hex, if it is, make it RGB
        if is_hex(in_col):
            self.col = hex_to_rgb(in_col)
            self._in_format = "hex"

        else:
            self.col = in_col
            self._in_format = "rgb"

    def get_format(self):
        """
        Return the format in which the input color was specified as a string.
        This could be "rgb" or "hex"
        """
        return self._in_format

    def info(self):
        """
        Print information about the color represented by the object.
        """
        print('Input (and output) color format: "%s"' % self.get_format())
        print("RGB: %s" % str(self.rgb()))
        print("HEX: %s" % str(self.hex()))
        print("HSL: %s" % str(self.hsl()))

    def hex(self):
        """
        Convenience function to get the hex value of a color.
        """
        return rgb_to_hex(self.col)  # type(self)(rgb_to_hex(self.col))

    def rgb(self):
        """
        Convenience function to get the rgb value of a color.
        """
        return self.col  # type(self)(self.col)

    def hsl(self):
        """
        Convenience function to get the hsl value of a color.
        """
        return rgb_to_hsl(self.col)  # type(self)(rgb_to_hsl(self.col))

    def set_h(self, value):
        """
        Set hue of color from 0 to 1 and return as new color.
        """
        assert 0 <= value <= 1
        h, s, l = self.hsl()
        if self.get_format == "hex":
            new_col = hsl_to_hex((value, s, l))
        else:
            new_col = hsl_to_rgb((value, s, l))
        return Color(new_col)

    def set_s(self, value):
        """
        Set saturation of color from 0 to 1 and return as new color.
        """
        assert 0 <= value <= 1
        h, s, l = self.hsl()
        if self.get_format == "hex":
            new_col = hsl_to_hex((h, value, l))
        else:
            new_col = hsl_to_rgb((h, value, l))
        return Color(new_col)

    def set_l(self, value):
        """
        Set lightness of color from 0 to 1 and return as new color.
        """
        assert 0 <= value <= 1
        h, s, l = self.hsl()
        if self.get_format == "hex":
            new_col = hsl_to_hex((h, s, value))
        else:
            new_col = hsl_to_rgb((h, s, value))
        return Color(new_col)

    def complementary(self):
        """
        Returns input color and its complementary color as a list of hex or
        rgb values, depending on what was submitted.

            O
           x x
          x   x
         x     x
          x   x
           x x
            O

        """

        # RGB -> HSL
        h, s, l = rgb_to_hsl(self.col)

        # Rotation by 180 degrees
        h = (h + 0.5) % 1
        color = hsl_to_rgb((h, s, l))  # HSL -> new RGB

        # Prepare colors for returning them
        if self.get_format() == "hex":
            colors = [rgb_to_hex(self.col), rgb_to_hex(tuple(color))]
        else:
            colors = [self.col, tuple(color)]

        # return as list of color objects
        return [Color(s) for s in colors]

    def split_complementary(self):
        """
        Returns input color and its split complementary colors (those adjecent to the complement)
        as a list of of hex or rgb values, depending on what was submitted.

            x
           O O
          x   x
         x     x
          x   x
           x x
            O


        """
        # RGB -> HSL
        h, s, l = rgb_to_hsl(self.col)

        # Rotation by 150 degrees
        angle = 150 / 360.0
        h_list = [(h + ang) % 1 for ang in (-angle, angle)]
        analagous = [hsl_to_rgb((h, s, l)) for h in h_list]  # HSL -> new RGB

        # add all the colors together
        colors = [self.col, tuple(analagous[0]), tuple(analagous[1])]

        # if the input was hex, convert it back
        if self.get_format() == "hex":
            colors = [rgb_to_hex(s) for s in colors]

        # return as list of color objects
        return [Color(s) for s in colors]

    def triadic(self):
        """
        Returns input color as well as the two triadic colors as a list of hex or rgb values, depending on what was submitted.

            x
           x x
          O   O
         x     x
          x   x
           x x
            O

        #first color is wrong!

        """

        # RGB -> HSL
        h, s, l = rgb_to_hsl(self.col)

        # Rotation by 120 degrees
        angle = 120 / 360.0
        h_list = [(h + ang) % 1 for ang in (-angle, angle)]

        analagous = [hsl_to_rgb((h, s, l)) for h in h_list]  # HSL -> new RGB

        # add all the colors together
        colors = [self.col, tuple(analagous[0]), tuple(analagous[1])]

        # if the input was hex, convert it back
        if self.get_format() == "hex":
            colors = [rgb_to_hex(s) for s in colors]

        # return as list of color objects
        return [Color(s) for s in colors]

    def square(self):
        """
           O
          x x
         x   x
        O     O
         x   x
          x x
           O
        """
        # RGB -> HSL
        h, s, l = rgb_to_hsl(self.col)

        # Rotation by 90 degrees
        angle = 90 / 360.0
        h_list = [(h + ang) % 1 for ang in (-angle, angle, angle * 2)]

        analagous = [hsl_to_rgb((h, s, l)) for h in h_list]  # HSL -> new RGB

        # add all the colors together
        colors = [
            self.col,
            tuple(analagous[0]),
            tuple(analagous[1]),
            tuple(analagous[2]),
        ]

        # if the input was hex, convert it back
        if self.get_format() == "hex":
            colors = [rgb_to_hex(s) for s in colors]

        # return as list of color objects
        return [Color(s) for s in colors]

    def tetradic(self):
        """
           O
          x x
         x   O
        x     x
         O   x
          x x
           O
        """
        # RGB -> HSL
        h, s, l = rgb_to_hsl(self.col)

        # Rotation by 30 degrees
        angle = 30 / 360.0
        h_list = [(h + ang) % 1 for ang in (-angle * 2, angle * 4, angle * 6)]

        analagous = [hsl_to_rgb((h, s, l)) for h in h_list]  # HSL -> new RGB

        # add all the colors together
        colors = [
            self.col,
            tuple(analagous[0]),
            tuple(analagous[1]),
            tuple(analagous[2]),
        ]

        # if the input was hex, convert it back
        if self.get_format() == "hex":
            colors = [rgb_to_hex(s) for s in colors]

        # return as list of color objects
        return [Color(s) for s in colors]

    def analagous(self):
        """
        Returns the input color as well as its analagous colors.

            x
           x x
          x   x
         x     x
          x   x
           O O
            O

        """
        # RGB -> HSL
        h, s, l = rgb_to_hsl(self.col)

        # Rotation by 30 degrees
        degree = 30 / 360.0
        h = [(h + angle) % 1 for angle in (-degree, degree)]
        analagous = [hsl_to_rgb((hi, s, l)) for hi in h]  # HSL -> new RGB

        # add all the colors together
        colors = [self.col, tuple(analagous[0]), tuple(analagous[1])]

        # if the input was hex, convert it back
        if self.get_format() == "hex":
            colors = [rgb_to_hex(s) for s in colors]

        # return as list of color objects
        return [Color(s) for s in colors]

    def similar(self):
        """
        Returns the input color as well as similar colors.
        (The ones that are next to the original one on the color wheel)
        """

        raise NotImplementedError

        # if the input was hex, convert it back
        if self.get_format() == "hex":
            colors = [rgb_to_hex(s) for s in colors]

        # return as list of color objects
        return [Color(s) for s in colors]

    def monochromatic(self):
        """
        Returns the input color as well as ....
        """

        raise NotImplementedError

        # if the input was hex, convert it back
        if self.get_format() == "hex":
            colors = [rgb_to_hex(s) for s in colors]

        # return as list of color objects
        return [Color(s) for s in colors]

    def tones(self, number=10):
        """
        Returns input color as well as
        tones - created by adding gray to a pure hue and showing less or more saturated options
        """
        raise NotImplementedError
        pass

    def tints(self, number=10):
        """
        Returns input color as well as tints of that color (lighter colors).
        number specifies how many new ones to return.
        """
        assert type(number) is int, "Error, the input number must be an integer."
        assert (
            2 <= number and number <= 1000
        ), "Error, the input number must be between 2 and 1000"

        # RGB -> HSL
        hue, saturation, lightness = rgb_to_hsl(self.col)

        # what is the difference of 100% lightness and the current value
        diff = 1.0 - lightness

        # devide the difference on a step size
        step = diff / float(number)

        # use that step size to generate the 10 increasing lightness values
        lightness_list = [lightness + step * s for s in range(1, number + 1)]

        # add the input color to a list, then build the 10 new HSL colors, convert to RGB and save in the same list
        colors = [self.col]
        colors.extend([hsl_to_rgb((hue, saturation, l)) for l in lightness_list])

        # if the input was hex, convert it back
        if self.get_format() == "hex":
            colors = [rgb_to_hex(s) for s in colors]

        # return as list of color objects
        return [Color(s) for s in colors]

    def shades(self, number=10):
        """
        Returns input color as well as shades of that color (darker colors).
        number specifies how many new ones to return.
        """
        assert type(number) is int, "Error, the input number must be an integer."
        assert (
            2 <= number and number <= 1000
        ), "Error, the input number must be between 2 and 1000"

        # RGB -> HSL
        hue, saturation, lightness = rgb_to_hsl(self.col)

        # divide the difference on a step size
        step = lightness / float(number)

        # use that step size to generate the 10 increasing lightness values
        lightness_list = [lightness - step * s for s in range(1, number + 1)]

        # add the input color to a list, then build the 10 new HSL colors,
        # convert to RGB and save in the same list
        colors = [self.col]
        colors.extend([hsl_to_rgb((hue, saturation, l)) for l in lightness_list])

        # if the input was hex, convert it back
        if self.get_format() == "hex":
            colors = [rgb_to_hex(s) for s in colors]

        # return as list of color objects
        return [Color(s) for s in colors]

    def saturate(self, number=10):
        """
        Returns the input color as well as more saturated versions of that color.
        number specifies how many new ones to return.
        """
        assert type(number) is int, "Error, the input number must be an integer."
        assert (
            2 <= number and number <= 1000
        ), "Error, the input number must be between 2 and 1000"

        # RGB -> HSL
        hue, saturation, lightness = rgb_to_hsl(self.col)

        # what is the difference of 100% saturation and the current value
        diff = 1.0 - saturation

        # divide the difference on a step size
        step = diff / float(number)

        # use that step size to generate the 10 increasing saturation values
        saturation_list = [saturation + step * s for s in range(1, number + 1)]

        # add the input color to a list, then build the 10 new HSL colors,
        # convert to RGB and save in the same list
        colors = [self.col]
        colors.extend([hsl_to_rgb((hue, s, lightness)) for s in saturation_list])

        # if the input was hex, convert it back
        if self.get_format() == "hex":
            colors = [rgb_to_hex(s) for s in colors]

        # return as list of color objects
        return [Color(s) for s in colors]

    def desaturate(self, number=10):
        """
        Returns the input color as well as less saturated versions of that color.
        number specifies how many new ones to return.
        """
        assert type(number) is int, "Error, the input number must be an integer."
        assert (
            2 <= number and number <= 1000
        ), "Error, the input number must be between 2 and 1000"

        # RGB -> HSL
        hue, saturation, lightness = rgb_to_hsl(self.col)

        # divide the difference on a step size
        step = saturation / float(number)

        # use that step size to generate the 10 increasing saturation values
        saturation_list = [saturation - step * s for s in range(1, number + 1)]

        # add the input color to a list, then build the 10 new HSL colors,
        # convert to RGB and save in the same list
        colors = [self.col]
        colors.extend([hsl_to_rgb((hue, s, lightness)) for s in saturation_list])

        # if the input was hex, convert it back
        if self.get_format() == "hex":
            colors = [rgb_to_hex(s) for s in colors]

        # return as list of color objects
        return [Color(s) for s in colors]

    def next_color(self):
        """
        Function for generating a sequence of unique colors.
        The input is a tuple of an RGB color, for example (124,1,34), and
        the method returns the "next" color.
        When R reaches 255 one is added to G and R is reset.
        When R and G both reach 255 one is added to B and R and G are reset.
        This should generate over 1.6 million colors (255*255*255)
        """
        R, G, B = self.col

        if R == 255 and G == 255 and B == 255:
            raise ValueError(
                "R, G and B all have the value 255, no further colors are " "available."
            )
        elif R == 255 and G == 255:
            R = 0
            G = 0
            B += 1
        elif R == 255:
            R = 0
            G += 1
        else:
            R += 1

        col = (R, G, B)

        # if the input was hex, convert it back
        if self.get_format() == "hex":
            col = rgb_to_hex(col)

        # return as color object
        return Color(col)


# def visualize(color_list=['#acc123','#ffffff','#000000', '#1ccf9c']):
#     """
#     Visualizes a list of colors.
#     Useful to see what one gets out of the different functions.
#     """
#
#     #asserts.... here....
#     #should work for list of strings and for color objects
#
#
#
#     from tkinter import Tk, Canvas, Frame, BOTH
#
#     color_list = [s.hex() for s in color_list]
#     print(color_list)
#
#     class Example(Frame):
#
#         def __init__(self, parent, cl):
#             Frame.__init__(self, parent)
#
#             self.parent = parent
#             self.color_list = cl
#             self.initUI()
#
#         def initUI(self):
#
#             self.parent.title("Colors")
#             self.pack(fill=BOTH, expand=1)
#
#             canvas = Canvas(self)
#
#             #modify rectangle size based on how many colors there are
#             rect_size = 700/float(len(color_list))
#
#             for i in range(len(self.color_list)):
#                 canvas.create_rectangle(10+rect_size*i, 10, 10+rect_size*(i+1), 110, outline=self.color_list[i], fill=self.color_list[i])
#             canvas.pack(fill=BOTH, expand=1)
#
#
#     def main():
#
#         root = Tk()
#         ex = Example(root, color_list)
#         root.geometry("720x120+250+300")
#         root.mainloop()
#
#     main()


def test():
    """
    Unit tests to make sure all methods work.
    """
    col1 = "#01f490"
    col2 = (1, 244, 144)
    col3 = (0.43141289437585734, 0.9918367346938776, 0.4803921568627451)

    # test helper functions
    assert is_rgb(col2) is True
    assert is_rgb(col1) is False
    assert is_rgb(col3) is False

    assert is_hex(col1) is True
    assert is_hex(col2) is False
    assert is_hex(col3) is False

    assert is_hsl(col3) is True
    assert is_hsl(col1) is False
    assert is_hsl(col2) is False

    assert rgb_to_hex(col2) == col1
    assert rgb_to_hsl(col2) == col3
    assert hex_to_rgb(col1) == col2
    assert hex_to_hsl(col1) == col3
    assert hsl_to_hex(col3) == col1
    assert hsl_to_rgb(col3) == col2

    # test the __eq__ method
    assert Color(col1) != Color(col2)
    assert Color(col1) != col2
    assert Color(col1) == Color(col1)
    assert Color(col1) == col1

    # test Color object with hex color
    x = Color(col1)
    assert x.rgb() == col2
    assert x.hex() == col1
    assert x.hsl() == col3
    assert x.get_format() == "hex"
    assert x.complementary() == ["#01f490", "#f40165"]
    assert x.split_complementary() == [
        "#01f490",
        "#f41601",
        "#f401de",
    ]  # these seem to be off by one
    assert x.triadic() == ["#01f490", "#f49001", "#9001f4"]
    assert x.square() == ["#01f490", "#def401", "#1601f4", "#f40165"]
    assert x.tetradic() == ["#01f490", "#65f401", "#9001f4", "#f40165"]
    assert x.analagous() == ["#01f490", "#01f417", "#01def4"]
    assert x.tints() == [
        "#01f490",
        "#11fe9d",
        "#2cfea8",
        "#46feb3",
        "#61febd",
        "#7bfec8",
        "#95ffd3",
        "#b0ffde",
        "#caffe9",
        "#e5fff4",
        "#ffffff",
    ]
    assert x.shades() == [
        "#01f490",
        "#01dc82",
        "#01c373",
        "#01ab65",
        "#019256",
        "#017a48",
        "#00623a",
        "#00492b",
        "#00311d",
        "#00180e",
        "#000000",
    ]
    assert x.saturate() == [
        "#01f490",
        "#01f490",
        "#01f490",
        "#01f490",
        "#01f490",
        "#00f490",
        "#00f590",
        "#00f590",
        "#00f590",
        "#00f590",
        "#00f590",
    ]
    assert x.desaturate() == [
        "#01f490",
        "#0de88e",
        "#19dc8c",
        "#25d08a",
        "#32c387",
        "#3eb785",
        "#4aab83",
        "#569f81",
        "#62937f",
        "#6e877d",
        "#7a7a7a",
    ]
    assert x.next_color() == "#02f490"
    # x.similar()
    # x.monochromatic()
    # x.tones()
    # x.set_h(0.5)
    # x.set_s(0.5)
    # x.set_l(0.5)

    # test Color object with rgb color
    x = Color(col2)
    assert x.rgb() == col2
    assert x.hex() == col1
    assert x.hsl() == col3
    assert x.get_format() == "rgb"
    assert x.complementary() == [(1, 244, 144), (244, 1, 101)]
    assert x.split_complementary() == [
        (1, 244, 144),
        (244, 22, 1),
        (244, 1, 222),
    ]  # these seem to be off by one
    assert x.triadic() == [(1, 244, 144), (244, 144, 1), (144, 1, 244)]
    assert x.square() == [(1, 244, 144), (222, 244, 1), (22, 1, 244), (244, 1, 101)]
    assert x.tetradic() == [(1, 244, 144), (101, 244, 1), (144, 1, 244), (244, 1, 101)]
    assert x.analagous() == [(1, 244, 144), (1, 244, 23), (1, 222, 244)]
    assert x.tints() == [
        (1, 244, 144),
        (17, 254, 157),
        (44, 254, 168),
        (70, 254, 179),
        (97, 254, 189),
        (123, 254, 200),
        (149, 255, 211),
        (176, 255, 222),
        (202, 255, 233),
        (229, 255, 244),
        (255, 255, 255),
    ]
    assert x.shades() == [
        (1, 244, 144),
        (1, 220, 130),
        (1, 195, 115),
        (1, 171, 101),
        (1, 146, 86),
        (1, 122, 72),
        (0, 98, 58),
        (0, 73, 43),
        (0, 49, 29),
        (0, 24, 14),
        (0, 0, 0),
    ]
    assert x.saturate() == [
        (1, 244, 144),
        (1, 244, 144),
        (1, 244, 144),
        (1, 244, 144),
        (1, 244, 144),
        (0, 244, 144),
        (0, 245, 144),
        (0, 245, 144),
        (0, 245, 144),
        (0, 245, 144),
        (0, 245, 144),
    ]
    assert x.desaturate() == [
        (1, 244, 144),
        (13, 232, 142),
        (25, 220, 140),
        (37, 208, 138),
        (50, 195, 135),
        (62, 183, 133),
        (74, 171, 131),
        (86, 159, 129),
        (98, 147, 127),
        (110, 135, 125),
        (122, 122, 122),
    ]
    assert x.next_color() == (2, 244, 144)
    # x.similar()
    # x.monochromatic()
    # x.tones()
    # x.set_h(0.5)
    # x.set_s(0.5)
    # x.set_l(0.5)

    print("All tests passed.")
