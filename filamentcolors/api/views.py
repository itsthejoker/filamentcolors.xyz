from colormath.color_objects import sRGBColor
from django.db.models import BooleanField, ExpressionWrapper, Q
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
    PantoneColorSerializer,
    RALColorSerializer,
    SwatchSerializer,
)
from filamentcolors.api.throttles import BurstRateThrottle, SustainedRateThrottle
from filamentcolors.colors import is_hex
from filamentcolors.models import RAL, FilamentType, Manufacturer, Pantone, Swatch


class CustomSwatchFilterBackend(DjangoFilterBackend):
    def get_filterset_kwargs(self, *args):
        # For lots of valid reasons, you're not really supposed
        # to do this. However, given that 'published' only has
        # two states, and it's reasonable to assume that most folks
        # will want one specific state, I'm making the executive
        # decision to apply a default for this field so that it
        # can be filtered against if someone really wants to.
        #
        # Read: me. I want to.
        kwargs = super().get_filterset_kwargs(*args)
        kwargs["data"]._mutable = True  # -sigh-
        if "published" not in kwargs["data"]:
            kwargs["data"]["published"] = True
        kwargs["data"]._mutable = False
        return kwargs


class SwatchViewSet(ReadOnlyModelViewSet):
    serializer_class = SwatchSerializer
    basename = "swatch"
    filter_backends = [CustomSwatchFilterBackend, OrderingFilter]
    filterset_fields = {
        "id": ["exact", "in"],
        "manufacturer": ["exact"],
        "manufacturer__name": ["exact", "icontains"],
        "manufacturer__id": ["exact"],
        "color_name": ["exact", "icontains"],
        "published": ["exact"],
        "color_parent": ["exact", "icontains"],
        "alt_color_parent": ["exact", "icontains"],
        "filament_type__parent_type__name": ["exact", "icontains"],
    }
    throttle_classes = [BurstRateThrottle, SustainedRateThrottle]

    def get_queryset(self):
        # `published` is set in the init
        queryset = Swatch.objects.annotate(
            is_available=ExpressionWrapper(
                Q(amazon_purchase_link__isnull=False)
                & Q(mfr_purchase_link__isnull=False),
                output_field=BooleanField(),
            )
        )
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
        Take a comma-separated list of hex colors and return the best guess for swatches.
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
        try:
            materials = [x.strip() for x in materials.split(",")]
        except AttributeError:
            materials = ["any"] * len(hex_colors)
        for color in hex_colors:
            if not is_hex(color):
                return JsonResponse(
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    data={"error": f"Color {color} is invalid."},
                )
        for count, color in enumerate(hex_colors):
            try:
                requested_material = materials[count]
            except IndexError:
                requested_material = None
            if (
                requested_material is not None
                and requested_material != "any"
                and requested_material != ""
            ):
                library = Swatch.objects.filter(
                    filters, filament_type__parent_type__name__iexact=requested_material
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
    filterset_fields = {"id": ["exact", "in"], "name": ["exact", "icontains"]}
    throttle_classes = [BurstRateThrottle, SustainedRateThrottle]


class FilamentTypeViewSet(ReadOnlyModelViewSet):
    serializer_class = FilamentTypeSerializer
    basename = "filament_type"
    queryset = FilamentType.objects.all().order_by(Lower("name"))
    throttle_classes = [BurstRateThrottle, SustainedRateThrottle]


class PantoneColorViewSet(ReadOnlyModelViewSet):
    serializer_class = PantoneColorSerializer
    basename = "pantone"
    queryset = Pantone.objects.all().order_by(Lower("name"))
    throttle_classes = [BurstRateThrottle, SustainedRateThrottle]


class RALColorViewSet(ReadOnlyModelViewSet):
    serializer_class = RALColorSerializer
    basename = "ral"
    queryset = RAL.objects.all().order_by(Lower("name"))
    throttle_classes = [BurstRateThrottle, SustainedRateThrottle]


def db_version(request):
    last_update_time = int(Swatch.objects.latest("date_added").date_added.timestamp())
    # db_version is a schema check. If the current schema provided to the API
    # ever changes, this number should be incremented by one. At this time,
    # there are no plans to support backwards compatible APIs, though I will
    # make an effort to communicate breaking changes well in advance as best
    # I can.
    return JsonResponse({"db_version": 1, "db_last_modified": last_update_time})
