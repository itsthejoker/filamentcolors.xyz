from django.shortcuts import render
from filamentcolors.models import Swatch
from filamentcolors.models import Printer
from django.utils import timezone

import colorsys

def homepage(request):
    html = 'home.html'

    recents = list(Swatch.objects.order_by('-pk'))
    # we don't need all of them, so trim the list to the 4 most recent.
    del recents[4:]

    return render(request, html, {'recents': recents})

def library(request):
    html = 'library.html'

    return render(request, html, {'swatches': Swatch.objects.all()})


def librarysort(request, method: str):
    """
    Available options:

    'type'
    'date added' <-- default
    'manufacturer'
    'color'

    Credit for color sort: https://stackoverflow.com/a/8915267

    :param request: the django request.
    :param method: the string which determines how to sort the results.
    :return:
    """

    def get_hsv(item):
        # TODO: I have NO idea if this works. Need to actually get some
        # samples up in here to check.
        hexrgb = item.hex_color
        r, g, b = (int(hexrgb[i:i + 2], 16) / 255.0 for i in range(0, 5, 2))
        return colorsys.rgb_to_hsv(r, g, b)

    items = Swatch.objects.all()
    if method == 'alphabetically':
        items.order_by('filament_type')

    elif method == 'manufacturer':
        items.order_by('-manufacturer')

    elif method == 'color':
        items = sorted(items, key=get_hsv)

    else:
        items.order_by('-date_added')

    return render(request, 'library.html', {'swatches': items})



def swatch_detail(request, id):
    html = 'swatch_detail.html'
    swatch = Swatch.objects.filter(id=id).first()
    if not swatch:
        return render(request, html, {'error': 'Swatch ID not found!'})
    else:
        return render(request, html, {'swatch': swatch})


def printer_detail(request, id):
    html = 'printer_detail.html'
    printer = Printer.objects.filter(id=id).first()
    if not printer:
        return render(request, html, {'error': 'Printer ID not found!'})
    else:
        return render(request, html, {'printer': printer})


def swatch_search(request):
    # TODO: create form for this sucker
    pass


def swatch_collection(request):
    """
    What I'm imagining for this is a way for people to select swatches and
    put them into a link that will just pull those items so that they can
    send options to other people. For example, maybe something like
    /library/collection/?swatches=1&34&23&7

    :param request: the Django request.
    :return: ¯\_(ツ)_/¯
    """

    pass


def about_page(request):
    html = 'about.html'
    return render(request, html)
