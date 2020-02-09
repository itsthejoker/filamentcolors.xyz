from rest_framework.viewsets import ReadOnlyModelViewSet
from django.db.models.functions import Lower
from filamentcolors.models import Swatch, Manufacturer, FilamentType
from filamentcolors.api.serializers import (
    SwatchSerializer,
    ManufacturerSerializer,
    FilamentTypeSerializer
)
from filamentcolors.helpers import get_hsv


class SwatchViewSet(ReadOnlyModelViewSet):
    serializer_class = SwatchSerializer
    basename = 'swatch'

    def get_queryset(self):
        queryset = Swatch.objects.all()
        # localhost:8000/api/swatch/?m=type
        method = self.request.query_params.get('m')  # for method
        if method == 'type':
            queryset = queryset.order_by('filament_type')

        elif method == 'manufacturer':
            queryset = queryset.order_by('manufacturer')

        elif method == 'color':
            queryset = sorted(queryset, key=get_hsv)

        else:
            queryset = queryset.order_by('-date_added')

        return queryset


class ManufacturerViewSet(ReadOnlyModelViewSet):
    serializer_class = ManufacturerSerializer
    basename = 'manufacturer'
    queryset = Manufacturer.objects.all().order_by(Lower('name'))

class FilamentTypeViewSet(ReadOnlyModelViewSet):
    serializer_class = FilamentTypeSerializer
    basename = 'filament_type'
    queryset = FilamentType.objects.all().order_by(Lower('name'))
