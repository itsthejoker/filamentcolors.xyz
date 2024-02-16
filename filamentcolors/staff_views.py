from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.shortcuts import HttpResponseRedirect, get_object_or_404, redirect, reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from filamentcolors.forms import (
    FilamentTypeForm,
    InventoryForm,
    ListSwatchInventoryForm,
    ManualHexValueForm,
    ManufacturerForm,
    SwatchForm,
    SwatchFormNoImages,
    SwatchUpdateImagesForm,
    RetailerForm,
    PurchaseLocationForm,
)
from filamentcolors.helpers import build_data_dict, prep_request
from filamentcolors.models import Swatch, PurchaseLocation


def get_path_redirect(request, viewname: str, *args, **kwargs):
    if path := request.META.get("HTTP_REFERER"):
        # reload the page we came from
        return redirect(path)
    else:
        return redirect(reverse(viewname, args=args, kwargs=kwargs))


@csrf_exempt
@staff_member_required
def set_colors_for_unpublished_swatches(request):
    if request.htmx and request.method == "POST":
        swatch = Swatch.objects.get(id=request.POST["swatch_id"])
        swatch.hex_color = request.POST["hex"]
        if swatch.hex_color.startswith("#"):
            swatch.hex_color = swatch.hex_color[1:]
        swatch.regenerate_all()
        swatch.save()
        return prep_request(
            request, "partials/success_alert.partial", {"swatch": swatch}
        )

    swatches = (
        Swatch.objects.select_related("manufacturer")
        .prefetch_related("filament_type")
        .filter(closest_pantone_1__isnull=True)
    )
    data = build_data_dict(request)
    data.update({"swatches": swatches})
    return prep_request(request, "standalone/update_swatch_colors.html", data)


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
    data = build_data_dict(request)
    data.update(
        {
            "header": "Swatch Add Form",
            "subheader": "A new splash of color!",
            "header_js_buttons": [
                {"text": "Manufacturer Search", "onclick": "loadMfrSearch()"},
                {"text": "Amazon Search", "onclick": "loadAmazonSearch()"},
            ],
            "header_link_buttons": [
                {"text": "Add New Manufacturer", "reverse_url": "add_mfr"},
                {"text": "Add Filament Type", "reverse_url": "add_filament_type"},
            ],
        }
    )
    if request.method == "POST":
        if swatch_id:
            form = SwatchForm(
                request.POST, request.FILES, instance=Swatch.objects.get(id=swatch_id)
            )
        else:
            form = SwatchForm(request.POST, request.FILES)
        try:
            new_swatch: Swatch = form.save(commit=False)
        except ValueError:
            messages.error(
                request,
                "The form was incomplete; please provide the missing information.",
            )
            data.update({"form": form})
            return prep_request(request, "generic_form.html", data)

        new_swatch.published = True
        new_swatch.date_published = timezone.now()
        new_swatch.save()
        return HttpResponseRedirect(
            reverse("swatchdetail", kwargs={"id": new_swatch.id})
        )
    else:
        if swatch_id:
            form = SwatchForm(instance=Swatch.objects.get(id=swatch_id))
        else:
            form = SwatchForm()

    data.update({"form": form})

    return prep_request(request, "generic_form.html", data)


@staff_member_required()
def add_swatch_landing(request):
    if request.method == "POST":
        form = ListSwatchInventoryForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            unpublished_swatch = data["unpublished_swatches"]
            colormatched_swatch = data["colormatched_swatches"]
            if unpublished_swatch and colormatched_swatch:
                messages.error(request, "You can only pick one swatch at a time!")
                return HttpResponseRedirect(reverse("add_swatch_landing"))
            theswatch = unpublished_swatch or colormatched_swatch
            return HttpResponseRedirect(
                reverse(
                    "add_swatch_from_inventory",
                    kwargs={"swatch_id": theswatch.id},
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
        return prep_request(request, "generic_form.html", data)


@staff_member_required
def update_swatch_images(request, swatch_id: int):
    target_swatch = Swatch.objects.get(id=swatch_id)
    if request.method == "POST":
        form = SwatchUpdateImagesForm(
            request.POST, request.FILES, instance=target_swatch
        )
        updated_swatch = form.save(commit=False)
        updated_swatch.crop_and_save_images()
        updated_swatch.save()
        return HttpResponseRedirect(
            reverse("swatchdetail", kwargs={"id": target_swatch.id})
        )
    else:
        data = build_data_dict(request)
        form = SwatchUpdateImagesForm(instance=target_swatch)
        data.update(
            {
                "header": "Update Swatch Images",
                "subheader": (
                    f"Updating images for {target_swatch.manufacturer.name}"
                    f" {target_swatch.color_name} {target_swatch.filament_type.name}!"
                ),
                "form": form,
            }
        )
        return prep_request(request, "generic_form.html", data)


@staff_member_required
def swatch_edit(request, swatch_id: int):
    target_swatch = Swatch.objects.get(id=swatch_id)
    if request.method == "POST":
        form = SwatchFormNoImages(request.POST, instance=target_swatch)
        updated_swatch = form.save(commit=False)
        updated_swatch.regenerate_info = True
        updated_swatch.save()

        return HttpResponseRedirect(
            reverse("swatchdetail", kwargs={"id": target_swatch.id})
        )
    else:
        data = build_data_dict(request)
        form = SwatchFormNoImages(instance=target_swatch)
        data.update(
            {
                "header": "Edit Swatch",
                "subheader": (
                    f"Edit {target_swatch.manufacturer.name}"
                    f"{target_swatch.manufacturer.get_possessive_apostrophe}"
                    f" {target_swatch.color_name} {target_swatch.filament_type.name}!"
                ),
                "form": form,
            }
        )
        return prep_request(request, "generic_form.html", data)


@staff_member_required
def add_inventory_swatch(request):
    # This is for adding a swatch that hasn't been printed yet.
    data = build_data_dict(request)
    data.update(
        {
            "header": "Inventory Add Form",
            "subheader": "Unpublished swatches to pull from later!",
            "header_link_buttons": [
                {"text": "Add New Manufacturer", "reverse_url": "add_mfr"},
                {"text": "Add Filament Type", "reverse_url": "add_filament_type"},
            ],
        }
    )
    if request.method == "POST":
        # we're probably going to be adding multiples at once, so we'll just
        # redirect back to this page.
        form = InventoryForm(request.POST)
        if not form.is_valid():
            messages.error(request, "The form doesn't look right; please try again.")
            data |= {"form": form}
            return prep_request(request, "generic_form.html", data)

        new_inventory = form.save(commit=False)
        new_inventory.published = False
        new_inventory.save()
        return get_path_redirect(request, "add_inventory")
    else:
        data |= {"form": InventoryForm()}
        return prep_request(request, "generic_form.html", data)


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
        return prep_request(request, "generic_form.html", data)


@staff_member_required
def add_retailer(request):
    if request.method == "POST":
        form = RetailerForm(request.POST)
        form.save()
        return get_path_redirect(request, "add_retailer")
    else:
        data = build_data_dict(request)
        form = RetailerForm()
        data.update(
            {
                "header": "Retailer Add Form",
                "subheader": "A new place that sells filament?",
                "form": form,
            }
        )
        return prep_request(request, "generic_form.html", data)


@staff_member_required
def add_purchase_location(request, swatch_id):
    swatch = Swatch.objects.get(id=swatch_id)
    if request.method == "POST":
        form = PurchaseLocationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            PurchaseLocation.objects.create(
                retailer_id=data["retailer"], swatch_id=swatch_id, url=data["url"]
            )
            return HttpResponseRedirect(
                reverse("view_purchase_locations", kwargs={"swatch_id": swatch_id})
            )
    else:
        data = build_data_dict(request)
        form = PurchaseLocationForm()
        data.update(
            {
                "header": "Purchase Location Form",
                "subheader": f"Where can we buy {swatch}?",
                "form": form,
            }
        )
        return prep_request(request, "generic_form.html", data)


@staff_member_required
def edit_purchase_location(request, swatch_id: int, location_id: int):
    target_location = PurchaseLocation.objects.get(swatch__id=swatch_id, id=location_id)
    if request.method == "POST":
        form = PurchaseLocationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            target_location.retailer_id = data["retailer"]
            target_location.url = data["url"]
            target_location.save()
            return HttpResponseRedirect(
                reverse("view_purchase_locations", kwargs={"swatch_id": swatch_id})
            )
        return HttpResponseRedirect(
            reverse(
                "edit_purchase_location",
                kwargs={"swatch_id": swatch_id, "location_id": location_id},
            )
        )
    else:
        data = build_data_dict(request)
        form = PurchaseLocationForm(
            initial={
                "url": target_location.url,
                "retailer": target_location.retailer.id,
            }
        )
        data.update(
            {
                "header": "Edit Swatch",
                "subheader": "Edit Purchase Location",
                "form": form,
            }
        )
        return prep_request(request, "generic_form.html", data)


@staff_member_required
def view_purchase_locations(request, swatch_id: int):
    data = build_data_dict(request)
    data["locations"] = PurchaseLocation.objects.filter(swatch__id=swatch_id)
    data["swatch_id"] = swatch_id
    return prep_request(request, "standalone/view_purchase_locations.html", data)


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
        return prep_request(request, "generic_form.html", data)


@staff_member_required
def recalculate_color(request, swatch_id: int):
    """Adds a quick link for redoing the color based on the long method."""
    swatch = get_object_or_404(Swatch, id=swatch_id)
    swatch.rebuild_long_way = True
    swatch.save()
    return HttpResponseRedirect(reverse("swatchdetail", kwargs={"id": swatch.id}))


@staff_member_required
def force_hex_color(request, swatch_id: int):
    """Allow manual setting of hex color if everything else fails."""
    swatch = get_object_or_404(Swatch, id=swatch_id)
    if request.method == "POST":
        form = ManualHexValueForm(request.POST)
        if form.is_valid():
            value = form.cleaned_data["hex_color"]
            if value.startswith("#"):
                value = value[1:]
            swatch.hex_color = value
            swatch.regenerate_all()
            swatch.update_all_color_matches(Swatch.objects.filter(published=True))
            swatch.save()
            return HttpResponseRedirect(
                reverse("swatchdetail", kwargs={"id": swatch.id})
            )
    form = ManualHexValueForm()
    return prep_request(request, "generic_form.html", {"form": form, "swatch": swatch})


@staff_member_required
def logout_view(request):
    logout(request)
    return get_path_redirect(request, "library")
