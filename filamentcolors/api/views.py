import colorsys

from colormath.color_conversions import convert_color
from colormath.color_objects import LabColor, sRGBColor
from django.db.models import F, Q
from django.db.models.functions import Lower
from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from filamentcolors.api.serializers import (
    FilamentTypeSerializer,
    ManufacturerSerializer,
    SwatchSerializer,
)
from filamentcolors.helpers import get_hsv
from filamentcolors.models import FilamentType, Manufacturer, Swatch


class SwatchViewSet(ReadOnlyModelViewSet):
    serializer_class = SwatchSerializer
    basename = "swatch"
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = {
        "manufacturer": ["exact"],
        "manufacturer__name": ["exact", "icontains"],
        "manufacturer__id": ["exact"],
        "color_name": ["exact", "icontains"],
        "published": ["exact"],
    }

    def get_queryset(self):
        queryset = Swatch.objects.filter(published=True)
        # localhost:8000/api/swatch/?m=type
        method = self.request.query_params.get("m")  # for method
        if method == "type":
            queryset = queryset.order_by("filament_type")

        elif method == "manufacturer":
            queryset = queryset.order_by("manufacturer")

        else:
            queryset = queryset.order_by("-date_added")

        return queryset

    @action(detail=False)
    def bulk_colormatch(self, request):
        """
        Take a comma separated list of hex colors and return the best guess for swatches.
        """
        hex_colors = self.request.query_params.get("colors")
        if not hex_colors:
            return Response(status.HTTP_422_UNPROCESSABLE_ENTITY)
        filters = Q(published=True)
        if filament_type_id := self.request.query_params.get("generic_type"):
            filters = filters & Q(filament_type__parent_type__id=int(filament_type_id))
        library = [s for s in Swatch.objects.filter(filters) if s.is_available()]

        results = {}
        hex_colors = [x.strip() for x in hex_colors.split(",")]
        for color in hex_colors:
            results[color] = Swatch()._get_closest_color_swatch(
                library,
                convert_color(sRGBColor.new_from_rgb_hex(color.strip()), LabColor),
            )

        results = {
            k: SwatchSerializer(v, context={"request": request}).data
            for k, v in results.items()
        }
        return JsonResponse(results)


class ManufacturerViewSet(ReadOnlyModelViewSet):
    serializer_class = ManufacturerSerializer
    basename = "manufacturer"
    queryset = Manufacturer.objects.all().order_by(Lower("name"))
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = {"id": ["exact"], "name": ["exact", "icontains"]}


class FilamentTypeViewSet(ReadOnlyModelViewSet):
    serializer_class = FilamentTypeSerializer
    basename = "filament_type"
    queryset = FilamentType.objects.all().order_by(Lower("name"))


def db_version(request):
    last_update_time = int(Swatch.objects.latest("date_added").date_added.timestamp())
    # db_version is a schema check. If the current schema provided to the API
    # ever changes, this number should be incremented by one. At this time,
    # there are no plans to support backwards compatible APIs, though I will
    # make an effort to communicate breaking changes well in advance as best
    # I can.
    return JsonResponse({"db_version": 1, "db_last_modified": last_update_time})
