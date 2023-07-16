from colormath.color_objects import sRGBColor
from django.db.models import Q
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
    PantoneColorSerializer,
    RALColorSerializer,
)
from filamentcolors.models import FilamentType, Manufacturer, Swatch, Pantone, RAL


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
            queryset = queryset.order_by("-date_published")

        return queryset

    @action(detail=False)
    def bulk_colormatch(self, request):
        """
        Take a comma separated list of hex colors and return the best guess for swatches.
        """
        hex_colors = self.request.query_params.get("colors")
        materials = self.request.query_params.get("materials")
        if not hex_colors:
            return Response(status.HTTP_422_UNPROCESSABLE_ENTITY)
        filters = Q(published=True) & (
            Q(mfr_purchase_link__isnull=True) | Q(amazon_purchase_link__isnull=True)
        )

        results = {}
        hex_colors = [x.strip() for x in hex_colors.split(",")]
        materials = [x.strip() for x in materials.split(",")]
        for count, color in enumerate(hex_colors):
            if (
                materials[count] is not None
                and materials[count] != "any"
                and materials[count] != ""
            ):
                library = Swatch.objects.filter(
                    filters, filament_type__parent_type__name__iexact=materials[count]
                )
            else:
                library = Swatch.objects.filter(filters)
            results[color] = Swatch().get_closest_color_swatch(
                library,
                sRGBColor.new_from_rgb_hex(color.strip()).get_upscaled_value_tuple(),
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


class PantoneColorViewSet(ReadOnlyModelViewSet):
    serializer_class = PantoneColorSerializer
    basename = "pantone"
    queryset = Pantone.objects.all().order_by(Lower("name"))


class RALColorViewSet(ReadOnlyModelViewSet):
    serializer_class = RALColorSerializer
    basename = "ral"
    queryset = RAL.objects.all().order_by(Lower("name"))


def db_version(request):
    last_update_time = int(Swatch.objects.latest("date_added").date_added.timestamp())
    # db_version is a schema check. If the current schema provided to the API
    # ever changes, this number should be incremented by one. At this time,
    # there are no plans to support backwards compatible APIs, though I will
    # make an effort to communicate breaking changes well in advance as best
    # I can.
    return JsonResponse({"db_version": 1, "db_last_modified": last_update_time})
