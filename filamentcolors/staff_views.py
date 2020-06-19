from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.shortcuts import HttpResponseRedirect, redirect, render, reverse

from filamentcolors.forms import (
    FilamentTypeForm,
    InventoryForm,
    ListSwatchInventoryForm,
    ManufacturerForm,
    SwatchForm,
)
from filamentcolors.helpers import build_data_dict
from filamentcolors.models import Swatch


def get_path_redirect(request, viewname: str, *args, **kwargs):
    if path := request.META.get("HTTP_REFERER"):
        # reload the page we came from
        return redirect(path)
    else:
        return redirect(reverse(viewname, args=args, kwargs=kwargs))


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
        data.update(
            {
                "header": "Swatch Add Form",
                "subheader": "A new splash of color!",
                "form": form,
            }
        )
        data.update(
            {
                "header_js_buttons": [
                    {"text": "Manufacturer Site", "onclick": "loadMfrSite()"},
                    {"text": "Amazon Search", "onclick": "loadAmazonSearch()"},
                ],
                "header_link_buttons": [
                    {"text": "Add New Manufacturer", "reverse_url": "add_mfr"},
                    {"text": "Add Filament Type", "reverse_url": "add_filament_type"},
                ],
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
                    "add_swatch_from_inventory",
                    kwargs={"swatch_id": form.cleaned_data["unpublished_swatches"].id},
                )
            )
    else:
        data = build_data_dict(request)
        form = ListSwatchInventoryForm()
        data.update(
            {
                "header": "Add a Swatch!",
                "subheader": (
                    "Are we building from scratch, pulling from inventory, or adding"
                    " a sample?"
                ),
                "form": form,
                "header_link_buttons": [
                    {"text": "Add sample to inventory", "reverse_url": "add_inventory"},
                    {"text": "Add from scratch", "reverse_url": "add_swatch"},
                ],
            }
        )
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
        return get_path_redirect(request, "add_inventory")
    else:
        data = build_data_dict(request)
        form = InventoryForm()
        data.update(
            {
                "header": "Inventory Add Form",
                "subheader": "Unpublished swatches to pull from later!",
                "form": form,
            }
        )
        return render(request, "generic_form.html", data)


@staff_member_required
def add_manufacturer(request):
    if request.method == "POST":
        form = ManufacturerForm(request.POST)
        form.save()
        return get_path_redirect(request, "add_swatch")
    else:
        data = build_data_dict(request)
        form = ManufacturerForm()
        data.update(
            {
                "header": "Manufacturer Add Form",
                "subheader": "A new source of color!",
                "form": form,
            }
        )
        return render(request, "generic_form.html", data)


@staff_member_required
def add_filament_type(request):
    if request.method == "POST":
        form = FilamentTypeForm(request.POST)
        form.save()
        return get_path_redirect(request, "add_swatch")
    else:
        data = build_data_dict(request)
        form = FilamentTypeForm()
        data.update(
            {
                "header": "Filament Type Add Form",
                "subheader": "A new type of color!",
                "form": form,
            }
        )
        return render(request, "generic_form.html", data)


@staff_member_required
def logout_view(request):
    logout(request)
    return get_path_redirect(request, "library")
