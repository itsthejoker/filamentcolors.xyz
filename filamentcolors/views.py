import random

from django.shortcuts import HttpResponseRedirect, redirect
from django.shortcuts import render
from django.shortcuts import reverse
from django.http import Http404
from django.contrib.auth import logout

from filamentcolors.helpers import get_hsv
from filamentcolors.helpers import set_tasty_cookies
from filamentcolors.helpers import show_welcome_modal
from filamentcolors.helpers import get_custom_library
from filamentcolors.models import Printer
from filamentcolors.models import Swatch
from filamentcolors.models import GenericFilamentType
from filamentcolors.helpers import build_data_dict
from filamentcolors.helpers import clean_collection_ids
from filamentcolors.helpers import generate_custom_library
from filamentcolors.helpers import get_swatches


def homepage(request):
    return HttpResponseRedirect(reverse('library'))


def librarysort(request, method: str=None):
    """
    Available options:

    'type'
    'date added' <-- default
    'manufacturer'
    'random'
    'color'

    Credit for color sort: https://stackoverflow.com/a/8915267

    :param request: the django request.
    :param method: the string which determines how to sort the results.
    :return:
    """
    html = 'library.html'

    data = build_data_dict(request, library=True)
    items = get_swatches(data)

    if method == 'type':
        items = items.order_by('filament_type')

    elif method == 'manufacturer':
        items = items.order_by('manufacturer')

    elif method == 'random':
        items = list(items)
        random.shuffle(items)

    elif method == 'color':
        items = sorted(items, key=get_hsv)
        data.update({'show_color_warning': True})

    else:
        items = items.order_by('-date_added')

    data.update({'swatches': items})

    if show_welcome_modal(request):
        data.update({'launch_welcome_modal': True})
        # https://stackoverflow.com/a/38798861
        response = render(None, html, data)
        set_tasty_cookies(response)
        return response

    return render(request, html, data)


def colorfamilysort(request, family_id):
    html = 'library.html'

    data = build_data_dict(request, library=True)
    s = get_swatches(data)

    s = s.filter(color_parent=family_id)

    data.update({'swatches': s})

    if show_welcome_modal(request):
        data.update({'launch_welcome_modal': True})
        response = render(None, html, data)
        set_tasty_cookies(response)
        return response

    return render(request, html, data)


def manufacturersort(request, id):
    html = 'library.html'

    data = build_data_dict(request, library=True)
    s = get_swatches(data)

    s = s.filter(manufacturer_id=id)

    if len(s) == 0:
        # No filaments found, and we shouldn't have a manufacturer
        # with no filaments.
        raise Http404

    data.update({'swatches': s})

    if show_welcome_modal(request):
        data.update({'launch_welcome_modal': True})
        response = render(None, html, data)
        set_tasty_cookies(response)
        return response

    return render(request, html, data)


def typesort(request, id):
    html = 'library.html'
    data = build_data_dict(request, library=True)

    f_type = GenericFilamentType.objects.filter(id=id).first()

    if not f_type:
        raise Http404

    s = get_swatches(data)

    s = s.filter(filament_type__parent_type=f_type)

    data.update({'swatches': s})

    if show_welcome_modal(request):
        data.update({'launch_welcome_modal': True})
        response = render(None, html, data)
        set_tasty_cookies(response)
        return response

    return render(request, html, data)

def swatch_detail(request, id):
    html = 'swatch_detail.html'
    swatch = Swatch.objects.filter(id=id).first()
    data = build_data_dict(request)

    if not swatch:
        raise Http404
    else:

        swatch.refresh_cache_if_needed()
        if generate_custom_library(data):
            swatch.update_all_color_matches(get_custom_library(data))

        data.update(
            {'swatch': swatch}
        )

        if show_welcome_modal(request):
            data.update({'launch_welcome_modal': True})
            response = render(None, html, data)
            set_tasty_cookies(response)
            return response

        return render(request, html, data)


def printer_detail(request, id):
    html = 'printer_detail.html'
    printer = Printer.objects.filter(id=id).first()
    if not printer:
        return render(request, html, {'error': 'Printer ID not found!'})
    else:
        return render(request, html, {'printer': printer})


def swatch_collection(request, ids):
    """
    What I'm imagining for this is a way for people to select swatches and
    put them into a link that will just pull those items so that they can
    send options to other people. For example, maybe something like
    /library/collection/1,34,23,7

    :param request: the Django request.
    :return: ¯\_(ツ)_/¯
    """
    data = build_data_dict(request, library=True)

    cleaned_ids = clean_collection_ids(ids)

    swatch_collection = list()

    for item in cleaned_ids:
        result = Swatch.objects.filter(id=item).first()
        if result:
            swatch_collection.append(result)

    data.update(
        {
            'swatches': swatch_collection,
            'collection_ids': ','.join([str(i) for i in cleaned_ids])
        }
    )

    return render(request, 'library.html', data)


def edit_swatch_collection(request, ids):
    html = 'library.html'
    data = build_data_dict(request, library=True)
    cleaned_ids = clean_collection_ids(ids)

    data.update({'preselect_collection': cleaned_ids})
    data.update({
        'swatches': Swatch.objects.all().order_by('-date_added'),
    })

    if show_welcome_modal(request):
        data.update({'launch_welcome_modal': True})
        response = render(None, html, data)
        set_tasty_cookies(response)
        return response

    return render(request, html, data)


def about_page(request):
    return render(request, 'about.html', build_data_dict(request))


def donation_page(request):
    return render(request, 'donations.html', build_data_dict(request))


def vrrf(request):
    return render(request, 'vrrf.html', build_data_dict(request))


def logout_view(request):
    logout(request)
    if path := request.META.get('HTTP_REFERER'):
        # reload the page we came from
        return redirect(path)
    else:
        return redirect(reverse('library'))
