from django import template

from filamentcolors.colors import hex_to_rgb

register = template.Library()


# https://stackoverflow.com/a/9948180
@register.simple_tag
def delta_e(obj_1, obj_2):
    return obj_1.get_distance_to(hex_to_rgb(obj_2.hex_color))
