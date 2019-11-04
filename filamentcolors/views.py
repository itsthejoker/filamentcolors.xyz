import random

from django.shortcuts import HttpResponseRedirect
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.shortcuts import reverse
from django.http import Http404

from filamentcolors.helpers import get_hsv
from filamentcolors.helpers import set_tasty_cookies
from filamentcolors.helpers import show_welcome_modal
from filamentcolors.models import Printer
from filamentcolors.models import Swatch
from filamentcolors.models import GenericFilamentType
from filamentcolors.helpers import build_data_dict
from filamentcolors.helpers import clean_collection_ids


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
    items = Swatch.objects.all()
    html = 'library.html'

    data = build_data_dict(request)

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
        response = render_to_response(html, data)
        set_tasty_cookies(response)
        return response

    return render(request, html, data)


def colorfamilysort(request, family_id):
    html = 'library.html'

    data = build_data_dict(request)

    s = Swatch.objects.filter(color_parent=family_id)

    if len(s) == 0:
        # There's no color family that matches the input. Something is wrong.
        raise Http404

    data.update({'swatches': s})

    if show_welcome_modal(request):
        data.update({'launch_welcome_modal': True})
        response = render_to_response(html, data)
        set_tasty_cookies(response)
        return response

    return render(request, html, data)


def manufacturersort(request, id):
    html = 'library.html'

    data = build_data_dict(request)

    s = Swatch.objects.filter(manufacturer_id=id)

    if len(s) == 0:
        # No filaments found, and we shouldn't have a manufacturer
        # with no filaments.
        raise Http404

    data.update({'swatches': s})

    if show_welcome_modal(request):
        data.update({'launch_welcome_modal': True})
        response = render_to_response(html, data)
        set_tasty_cookies(response)
        return response

    return render(request, html, data)


def typesort(request, id):
    html = 'library.html'
    data = build_data_dict(request)

    f_type = GenericFilamentType.objects.filter(id=id).first()

    if not f_type:
        raise Http404

    s = Swatch.objects.filter(filament_type__parent_type=f_type)

    data.update({'swatches': s})

    if show_welcome_modal(request):
        data.update({'launch_welcome_modal': True})
        response = render_to_response(html, data)
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

        data.update(
            {'swatch': swatch}
        )

        if show_welcome_modal(request):
            data.update({'launch_welcome_modal': True})
            response = render_to_response(html, data)
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
    data = build_data_dict(request)

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
    data = build_data_dict(request)
    cleaned_ids = clean_collection_ids(ids)

    data.update({'preselect_collection': cleaned_ids})
    data.update({
        'swatches': Swatch.objects.all().order_by('-date_added'),
    })

    if show_welcome_modal(request):
        data.update({'launch_welcome_modal': True})
        response = render_to_response(html, data)
        set_tasty_cookies(response)
        return response

    return render(request, html, data)

def about_page(request):
    html = 'about.html'
    return render(request, html, build_data_dict(request))


def handler404(request, exception, template_name="404.html"):
    response = render_to_response("404.html", build_data_dict(request))
    response.status_code = 404
    return response


def handler500(request, exception, template_name="500.html"):
    response = render_to_response("500.html", build_data_dict(request))
    response.status_code = 500
    return response
