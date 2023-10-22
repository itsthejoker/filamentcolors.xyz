from django import template


register = template.Library()


# https://stackoverflow.com/a/9948180
@register.filter
def subtract(value, arg):
    return value - arg
