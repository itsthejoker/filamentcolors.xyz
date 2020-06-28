from django import forms
from django.db.models.functions import Lower

from filamentcolors.models import FilamentType, Manufacturer, Swatch


class SwatchForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
            "filament_type",
            "color_parent",
            "amazon_purchase_link",
            "mfr_purchase_link",
            "image_front",
            "image_back",
            "image_other",
            "notes",
            "donated_by",
            "tags",
        ]


class ListSwatchInventoryForm(forms.Form):
    unpublished_swatches = forms.ModelChoiceField(
        Swatch.objects.exclude(published=True)
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
