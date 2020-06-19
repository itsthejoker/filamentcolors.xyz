import random

from django.contrib.auth import logout
from django.http import Http404
from django.shortcuts import HttpResponseRedirect, redirect
from django.shortcuts import render
from django.shortcuts import reverse
from django.contrib.admin.views.decorators import staff_member_required

from filamentcolors.helpers import build_data_dict
from filamentcolors.helpers import clean_collection_ids
from filamentcolors.helpers import generate_custom_library
from filamentcolors.helpers import get_custom_library
from filamentcolors.helpers import get_hsv
from filamentcolors.helpers import get_swatches
from filamentcolors.helpers import set_tasty_cookies
from filamentcolors.helpers import show_welcome_modal
from filamentcolors.models import GenericFilamentType
from filamentcolors.models import Swatch
from filamentcolors.forms import (
    FilamentTypeForm, InventoryForm, ListSwatchInventoryForm, ManufacturerForm, SwatchForm
)


def homepage(request):
    return HttpResponseRedirect(reverse('library'))


def librarysort(request, method: str = None):
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
            'collection_ids': ','.join([str(i) for i in cleaned_ids]),
            'show_collection_edit_button': True
        }
    )

    return render(request, 'library.html', data)


def edit_swatch_collection(request, ids):
    html = 'library.html'
    data = build_data_dict(request, library=True)
    cleaned_ids = clean_collection_ids(ids)

    data.update({'preselect_collection': cleaned_ids})
    data.update({
        'swatches': get_swatches(data).order_by('-date_added'),
    })

    if show_welcome_modal(request):
        data.update({'launch_welcome_modal': True})
        response = render(None, html, data)
        set_tasty_cookies(response)
        return response

    return render(request, html, data)


@staff_member_required
def add_swatch(request, swatch_id: int = None):
    """
    This handles serving the form for adding a swatch and saving that form.

    We can call the form in two different ways:
        1) we want to start from scratch, in which case a swatch_id will not
            be provided and we'll serve a blank form & save a new element.
        2) we want to start from inventory, in which case we'll have a swatch_id
            and we'll want to make sure that we save over that inventory element
            when we finish filling it out.
    """
    if request.method == "POST":
        if swatch_id:
            form = SwatchForm(
                request.POST, request.FILES, instance=Swatch.objects.get(id=swatch_id)
            )
        else:
            form = SwatchForm(request.POST, request.FILES)
        new_swatch = form.save(commit=False)
        new_swatch.published = True
        new_swatch.save()
        return HttpResponseRedirect(
            reverse("swatchdetail", kwargs={"id": new_swatch.id})
        )
    else:
        if swatch_id:
            form = SwatchForm(instance=Swatch.objects.get(id=swatch_id))
        else:
            form = SwatchForm()
        data = build_data_dict(request)
        data.update({
            "header": "Swatch Add Form",
            "subheader": "A new splash of color!",
            "form": form
        })
        data.update(
            {
                "header_js_buttons": [
                    {
                        "text": "Manufacturer Site",
                        "onclick": "loadMfrSite()"
                    },
                    {
                        "text": "Amazon Search",
                        "onclick": "loadAmazonSearch()"
                    }
                ],
                "header_link_buttons": [
                    {
                        "text": "Add New Manufacturer",
                        "reverse_url": "add_mfr"
                    },
                    {
                        "text": "Add Filament Type",
                        "reverse_url": "add_filament_type"
                    }
                ]
            }
        )
    return render(request, "generic_form.html", data)


@staff_member_required()
def add_swatch_landing(request):
    if request.method == "POST":
        form = ListSwatchInventoryForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(
                reverse(
                    'add_swatch_from_inventory',
                    kwargs={
                        "swatch_id": form.cleaned_data['unpublished_swatches'].id
                    }
                )
            )
    else:
        data = build_data_dict(request)
        form = ListSwatchInventoryForm()
        data.update({
            "header": "Add a Swatch!",
            "subheader": "Are we building from scratch or pulling from inventory?",
            "form": form,
            "header_link_buttons": [
                {
                    "text": "Add from scratch",
                    "reverse_url": "add_swatch"
                }
            ]
        })
        return render(request, "generic_form.html", data)


@staff_member_required
def add_inventory_swatch(request):
    # This is for adding a swatch that hasn't been printed yet.
    if request.method == "POST":
        # we're probably going to be adding multiples at once, so we'll just
        # redirect back to this page.
        form = InventoryForm(request.POST)
        new_inventory = form.save(commit=False)
        new_inventory.published = False
        new_inventory.save()
        return HttpResponseRedirect(reverse("add_inventory"))
    else:
        data = build_data_dict(request)
        form = InventoryForm()
        data.update({
            "header": "Inventory Add Form",
            "subheader": "Unpublished swatches to pull from later!",
            "form": form
        })
        return render(request, "generic_form.html", data)


@staff_member_required
def add_manufacturer(request):
    if request.method == "POST":
        form = ManufacturerForm(request.POST)
        form.save()
        return HttpResponseRedirect(reverse("add_swatch"))
    else:
        data = build_data_dict(request)
        form = ManufacturerForm()
        data.update({
            "header": "Manufacturer Add Form",
            "subheader": "A new source of color!",
            "form": form
        })
        return render(request, "generic_form.html", data)


@staff_member_required
def add_filament_type(request):
    if request.method == "POST":
        form = FilamentTypeForm(request.POST)
        form.save()
        return HttpResponseRedirect(reverse("add_swatch"))
    else:
        data = build_data_dict(request)
        form = FilamentTypeForm()
        data.update({
            "header": "Filament Type Add Form",
            "subheader": "A new type of color!",
            "form": form
        })
        return render(request, "generic_form.html", data)


def about_page(request):
    return render(request, 'about.html', build_data_dict(request))


def donation_page(request):
    return render(request, 'donations.html', build_data_dict(request))


@staff_member_required
def logout_view(request):
    logout(request)
    if path := request.META.get('HTTP_REFERER'):
        # reload the page we came from
        return redirect(path)
    else:
        return redirect(reverse('library'))
