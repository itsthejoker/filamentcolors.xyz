from rest_framework.serializers import HyperlinkedModelSerializer

from filamentcolors.models import Swatch, Manufacturer, FilamentType
from filamentcolors.api.taggit_serializer import (
    TaggitSerializer,
    TagListSerializerField
)


class FilamentTypeSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = FilamentType
        fields = (
            'id',
            'name',
            'hot_end_temp',
            'bed_temp'
        )


class ManufacturerSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Manufacturer
        fields = (
            'id',
            'name',
        )


class SwatchSerializer(TaggitSerializer, HyperlinkedModelSerializer):
    manufacturer = ManufacturerSerializer(read_only=True)
    filament_type = FilamentTypeSerializer(read_only=True)

    tags = TagListSerializerField()

    class Meta:
        model = Swatch
        fields = (
            'id',
            'manufacturer',
            'color_name',
            'filament_type',
            'color_parent',
            'image_front',
            'image_back',
            'image_other',
            'date_added',
            'notes',
            'amazon_purchase_link',
            'mfr_purchase_link',
            'complement',
            'analogous_1',
            'analogous_2',
            'triadic_1',
            'triadic_2',
            'split_complement_1',
            'split_complement_2',
            'tetradic_1',
            'tetradic_2',
            'tetradic_3',
            'square_1',
            'square_2',
            'square_3',
            'tags',
            'card_img',
            'hex_color',
            'complement_hex',
            'human_readable_date'
        )
