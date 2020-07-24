import random

from django.http import Http404
from django.shortcuts import HttpResponseRedirect, render, reverse, get_object_or_404

from filamentcolors.helpers import (
    build_data_dict,
    clean_collection_ids,
    generate_custom_library,
    get_custom_library,
    get_hsv,
    get_swatches,
    set_tasty_cookies,
    show_welcome_modal,
)
from filamentcolors.models import GenericFilamentType, Swatch, Post


def homepage(request):
    return HttpResponseRedirect(reverse("library"))


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
    html = "library.html"

    data = build_data_dict(request, library=True)
    items = get_swatches(data)

    if method == "type":
        items = items.order_by("filament_type")

    elif method == "manufacturer":
        items = items.order_by("manufacturer")

    elif method == "random":
        items = list(items)
        random.shuffle(items)

    elif method == "color":
        items = sorted(items, key=get_hsv)
        data.update({"show_color_warning": True})

    else:
        items = items.order_by("-date_added")

    data.update({"swatches": items})

    if show_welcome_modal(request):
        data.update({"launch_welcome_modal": True})
        # https://stackoverflow.com/a/38798861
        response = render(None, html, data)
        set_tasty_cookies(response)
        return response

    return render(request, html, data)


def colorfamilysort(request, family_id):
    html = "library.html"

    data = build_data_dict(request, library=True)
    s = get_swatches(data)

    s = s.filter(color_parent=family_id)

    data.update({"swatches": s})

    if show_welcome_modal(request):
        data.update({"launch_welcome_modal": True})
        response = render(None, html, data)
        set_tasty_cookies(response)
        return response

    return render(request, html, data)


def manufacturersort(request, id):
    html = "library.html"

    data = build_data_dict(request, library=True)
    s = get_swatches(data)

    s = s.filter(manufacturer_id=id)

    if len(s) == 0:
        # No filaments found, and we shouldn't have a manufacturer
        # with no filaments.
        raise Http404

    data.update({"swatches": s})

    if show_welcome_modal(request):
        data.update({"launch_welcome_modal": True})
        response = render(None, html, data)
        set_tasty_cookies(response)
        return response

    return render(request, html, data)


def typesort(request, id):
    html = "library.html"
    data = build_data_dict(request, library=True)

    f_type = GenericFilamentType.objects.filter(id=id).first()

    if not f_type:
        raise Http404

    s = get_swatches(data)

    s = s.filter(filament_type__parent_type=f_type)

    data.update({"swatches": s})

    if show_welcome_modal(request):
        data.update({"launch_welcome_modal": True})
        response = render(None, html, data)
        set_tasty_cookies(response)
        return response

    return render(request, html, data)


def swatch_detail(request, id):
    html = "swatch_detail.html"
    swatch = Swatch.objects.filter(id=id).first()
    data = build_data_dict(request)

    if not swatch:
        raise Http404
    else:

        swatch.refresh_cache_if_needed()
        if generate_custom_library(data):
            swatch.update_all_color_matches(get_custom_library(data))

        data.update({"swatch": swatch})

        if show_welcome_modal(request):
            data.update({"launch_welcome_modal": True})
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
            "swatches": swatch_collection,
            "collection_ids": ",".join([str(i) for i in cleaned_ids]),
            "show_collection_edit_button": True,
        }
    )

    return render(request, "library.html", data)


def edit_swatch_collection(request, ids):
    html = "library.html"
    data = build_data_dict(request, library=True)
    cleaned_ids = clean_collection_ids(ids)

    data.update({"preselect_collection": cleaned_ids})
    data.update(
        {"swatches": get_swatches(data).order_by("-date_added"),}
    )

    if show_welcome_modal(request):
        data.update({"launch_welcome_modal": True})
        response = render(None, html, data)
        set_tasty_cookies(response)
        return response

    return render(request, html, data)


def inventory_page(request):
    data = build_data_dict(request)
    data.update({
        "swatches": Swatch.objects.all(),
    })
    return render(request, "inventory.html", data)


def post_list(request):
    data = build_data_dict(request)
    data.update({
        "posts": Post.objects.filter(published=True).order_by('-date_added'),
    })
    return render(request, "post_list.html", data)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if not post.published:
        raise Http404
    data = build_data_dict(request)
    data.update({"post": post})
    return render(request, "post_detail.html", data)


def post_preview(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if not post.enable_preview:
        raise Http404
    data = build_data_dict(request)
    data.update({"post": post})
    return render(request, "post_detail.html", data)


def about_page(request):
    return render(request, "about.html", build_data_dict(request))


def donation_page(request):
    return render(request, "donations.html", build_data_dict(request))


def error_404(request, *args, **kwargs):
    return render(request, "404.html", build_data_dict(request), status=404)


def error_500(request, *args, **kwargs):
    return render(request, "500.html", build_data_dict(request), status=500)
