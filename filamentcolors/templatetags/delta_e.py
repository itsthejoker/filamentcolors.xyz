from django import template

from filamentcolors.colors import hex_to_rgb

register = template.Library()


# https://stackoverflow.com/a/9948180
@register.simple_tag
def delta_e(obj_1, obj_2):
    if hasattr(obj_2, "lab_l") and obj_2.lab_l is not None:
        return obj_1.get_distance_to((obj_2.lab_l, obj_2.lab_a, obj_2.lab_b))
    return obj_1.get_distance_to(hex_to_rgb(obj_2.hex_color))
