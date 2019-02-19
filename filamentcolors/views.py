from django.shortcuts import render
from filamentcolors.models import Swatch
from filamentcolors.models import Printer
from django.utils import timezone
from filamentcolors.helpers import get_hsv
from filamentcolors.helpers import get_complement_swatch

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
    items = Swatch.objects.all()
    if method == 'type':
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

    c_swatch = get_complement_swatch(swatch)

    if not swatch:
        return render(request, html, {'error': 'Swatch ID not found!'})
    else:
        return render(
            request, html, {'swatch': swatch, 'c_swatch': c_swatch}
        )


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
