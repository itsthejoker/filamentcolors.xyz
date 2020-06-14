from django import forms
from filamentcolors.models import Swatch

class SwatchForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image_front'].required = True
        self.fields['image_back'].required = True

    class Meta:
        model = Swatch
        fields = [
            "manufacturer",
            "color_name",
            "filament_type",
            "color_parent",
            "image_front",
            "image_back",
            "image_other",
            "notes",
            "amazon_purchase_link",
            "mfr_purchase_link",
            "tags"
        ]
