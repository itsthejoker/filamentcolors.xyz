from typing import Optional

from rest_framework import serializers
from rest_framework.serializers import HyperlinkedModelSerializer
from taggit.serializers import TagListSerializerField

from filamentcolors.models import (
    RAL,
    FilamentType,
    Manufacturer,
    Pantone,
    Swatch,
    PantonePMS,
)


class FilamentTypeSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = FilamentType
        fields = ("id", "name", "hot_end_temp", "bed_temp")


class ManufacturerSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Manufacturer
        fields = ("id", "name", "website")


class ColorSerializerHelpers:
    def get_name(self, obj) -> Optional[str]:
        if obj.name:
            return obj.name
        return None

    def get_hex_color(self, obj) -> str:
        return f"#{obj.hex_color}"


class PantoneColorSerializer(HyperlinkedModelSerializer, ColorSerializerHelpers):
    name = serializers.SerializerMethodField()
    hex_color = serializers.SerializerMethodField()

    class Meta:
        model = Pantone
        fields = ("code", "name", "hex_color", "category")


class PantonePMSSerializer(HyperlinkedModelSerializer, ColorSerializerHelpers):
    hex_color = serializers.SerializerMethodField()

    class Meta:
        model = PantonePMS
        fields = ("code", "hex_color")


class RALColorSerializer(HyperlinkedModelSerializer, ColorSerializerHelpers):
    name = serializers.SerializerMethodField()
    hex_color = serializers.SerializerMethodField()

    class Meta:
        model = RAL
        fields = ("code", "name", "hex_color", "category")


class SwatchSerializer(HyperlinkedModelSerializer):
    manufacturer = ManufacturerSerializer(read_only=True)
    filament_type = FilamentTypeSerializer(read_only=True)
    closest_pantone_1 = PantoneColorSerializer(read_only=True)
    closest_pantone_2 = PantoneColorSerializer(read_only=True)
    closest_pantone_3 = PantoneColorSerializer(read_only=True)
    closest_ral_3 = RALColorSerializer(read_only=True)
    closest_ral_2 = RALColorSerializer(read_only=True)
    closest_ral_1 = RALColorSerializer(read_only=True)
    closest_pms_1 = PantonePMSSerializer(read_only=True)
    closest_pms_2 = PantonePMSSerializer(read_only=True)
    closest_pms_3 = PantonePMSSerializer(read_only=True)

    tags = TagListSerializerField()

    class Meta:
        model = Swatch
        fields = (
            "id",
            "manufacturer",
            "color_name",
            "filament_type",
            "color_parent",
            "image_front",
            "image_back",
            "image_other",
            "date_added",
            "date_published",
            "notes",
            "amazon_purchase_link",
            "mfr_purchase_link",
            "closest_pantone_1",
            "closest_pantone_2",
            "closest_pantone_3",
            "closest_pms_1",
            "closest_pms_2",
            "closest_pms_3",
            "closest_ral_1",
            "closest_ral_2",
            "closest_ral_3",
            "complement",
            "analogous_1",
            "analogous_2",
            "triadic_1",
            "triadic_2",
            "split_complement_1",
            "split_complement_2",
            "tetradic_1",
            "tetradic_2",
            "tetradic_3",
            "square_1",
            "square_2",
            "square_3",
            "closest_1",
            "closest_2",
            "tags",
            "card_img",
            "hex_color",
            "human_readable_date",
            "is_available",
        )
