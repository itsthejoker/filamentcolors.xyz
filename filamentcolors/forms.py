from django import forms
from django.db.models.functions import Lower
from django.forms import ClearableFileInput

from filamentcolors.models import FilamentType, Manufacturer, Swatch


class CustomClearableFileInputField(ClearableFileInput):
    template_name = "widgets/clearable_file_input.html"


class SwatchForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["hex_color"].required = True
        self.fields["image_front"].required = True
        self.fields["image_back"].required = True

    manufacturer = forms.ModelChoiceField(
        queryset=Manufacturer.objects.all().order_by(Lower("name"))
    )
    filament_type = forms.ModelChoiceField(
        queryset=FilamentType.objects.all().order_by(Lower("name"))
    )

    class Meta:
        model = Swatch
        fields = [
            "manufacturer",
            "color_name",
            "hex_color",
            "filament_type",
            "color_parent",
            "alt_color_parent",
            "amazon_purchase_link",
            "mfr_purchase_link",
            "image_front",
            "image_back",
            "image_other",
            "notes",
            "donated_by",
        ]
        widgets = {
            "image_front": CustomClearableFileInputField,
            "image_back": CustomClearableFileInputField,
            "image_other": CustomClearableFileInputField,
        }


class SwatchFormNoImages(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["hex_color"].required = True
        self.fields["color_name"].required = True
        self.fields["manufacturer"].required = True
        self.fields["filament_type"].required = True
        self.fields["color_parent"].required = True

    manufacturer = forms.ModelChoiceField(
        queryset=Manufacturer.objects.all().order_by(Lower("name"))
    )
    filament_type = forms.ModelChoiceField(
        queryset=FilamentType.objects.all().order_by(Lower("name"))
    )

    class Meta:
        model = Swatch
        fields = [
            "manufacturer",
            "color_name",
            "hex_color",
            "filament_type",
            "color_parent",
            "alt_color_parent",
            "amazon_purchase_link",
            "mfr_purchase_link",
            "notes",
            "donated_by",
        ]


class SwatchUpdateImagesForm(forms.ModelForm):
    class Meta:
        model = Swatch
        fields = [
            "image_front",
            "image_back",
            "image_other",
        ]
        widgets = {
            "image_front": CustomClearableFileInputField,
            "image_back": CustomClearableFileInputField,
            "image_other": CustomClearableFileInputField,
        }


class ListSwatchInventoryForm(forms.Form):
    unpublished_swatches = forms.ModelChoiceField(
        Swatch.objects.select_related("manufacturer")
        .prefetch_related("filament_type")
        .filter(published=False)
        .order_by(Lower("manufacturer__name"))
    )


class ManufacturerForm(forms.ModelForm):
    class Meta:
        model = Manufacturer
        fields = ["name", "website"]


class FilamentTypeForm(forms.ModelForm):
    class Meta:
        model = FilamentType
        fields = ["name", "hot_end_temp", "bed_temp", "parent_type"]


class InventoryForm(forms.ModelForm):
    manufacturer = forms.ModelChoiceField(
        queryset=Manufacturer.objects.all().order_by(Lower("name"))
    )
    filament_type = forms.ModelChoiceField(
        queryset=FilamentType.objects.all().order_by(Lower("name"))
    )

    class Meta:
        model = Swatch
        fields = [
            "filament_type",
            "color_name",
            "color_parent",
            "manufacturer",
            "donated_by",
        ]


class ManualHexValueForm(forms.Form):
    hex_color = forms.CharField(
        max_length=7,
        help_text="Use the color picker out of the dev tools in FF or use the eyedropper.",
    )
