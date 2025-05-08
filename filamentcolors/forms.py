from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.functions import Lower
from django.forms import ClearableFileInput, TextInput

from filamentcolors.constants import LAB
from filamentcolors.models import FilamentType, Manufacturer, Retailer, Swatch


class CustomClearableFileInputField(ClearableFileInput):
    template_name = "widgets/clearable_file_input.html"


class SwatchForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["lab_l"].required = True
        self.fields["lab_a"].required = True
        self.fields["lab_b"].required = True
        self.fields["image_front"].required = True
        self.fields["image_back"].required = True
        self.fields["manufacturer"].widget.attrs.update({"autofocus": "autofocus"})

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
            "lab_l",
            "lab_a",
            "lab_b",
            "td",
            "color_parent",
            "alt_color_parent",
            "manufacturer",
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
            "td": TextInput(),
        }


class SwatchFormNoImages(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["lab_l"].required = True
        self.fields["lab_a"].required = True
        self.fields["lab_b"].required = True
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
    td = forms.FloatField(required=False)

    class Meta:
        model = Swatch
        fields = [
            "manufacturer",
            "color_name",
            "lab_l",
            "lab_a",
            "lab_b",
            "computed_lab",
            "td",
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
    _qs = (
        Swatch.objects.select_related("manufacturer")
        .prefetch_related("filament_type")
        .filter(published=False)
        .order_by(Lower("manufacturer__name"), Lower("color_name"))
    )
    colormatched_swatches = forms.ModelChoiceField(
        _qs.exclude(hex_color__exact=""), required=False
    )
    unpublished_swatches = forms.ModelChoiceField(_qs.filter(), required=False)


class ManufacturerForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update({"autofocus": "autofocus"})

    class Meta:
        model = Manufacturer
        fields = ["name", "website"]


class RetailerForm(forms.ModelForm):
    class Meta:
        model = Retailer
        fields = "__all__"


class PurchaseLocationForm(forms.Form):
    retailer = forms.ModelChoiceField(queryset=Retailer.objects.all())
    url = forms.URLField()


class FilamentTypeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update({"autofocus": "autofocus"})

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["filament_type"].widget.attrs.update(
            {"autofocus": "autofocus", "required": "required"}
        )

    class Meta:
        model = Swatch
        fields = [
            "filament_type",
            "color_name",
            "color_parent",
            "alt_color_parent",
            "manufacturer",
            "donated_by",
        ]


class ManualLabValueForm(forms.Form):
    lab_l = forms.FloatField(
        min_value=LAB["L"]["min"],
        max_value=LAB["L"]["max"],
        validators=[
            MinValueValidator(LAB["L"]["min"]),
            MaxValueValidator(LAB["L"]["max"]),
        ],
    )
    lab_a = forms.FloatField(
        min_value=LAB["A"]["min"],
        max_value=LAB["A"]["max"],
        validators=[
            MinValueValidator(LAB["A"]["min"]),
            MaxValueValidator(LAB["A"]["max"]),
        ],
    )
    lab_b = forms.FloatField(
        min_value=LAB["B"]["min"],
        max_value=LAB["B"]["max"],
        validators=[
            MinValueValidator(LAB["B"]["min"]),
            MaxValueValidator(LAB["B"]["max"]),
        ],
    )
