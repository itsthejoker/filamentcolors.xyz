import random

from colormath.color_objects import LabColor, sRGBColor
from django.db.models import BooleanField, ExpressionWrapper, Q
from django.db.models.functions import Lower
from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination
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
from filamentcolors.helpers import annotate_with_calculated_td, get_hsv, get_new_seed
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


class SmallPageNumberPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = "page_size"
    max_page_size = 100


class SwatchViewSet(ReadOnlyModelViewSet):
    serializer_class = SwatchSerializer
    basename = "swatch"
    filter_backends = [CustomSwatchFilterBackend, OrderingFilter]
    filterset_fields = {
        "id": ["exact", "in"],
        "manufacturer": ["exact"],
        "manufacturer__name": ["exact", "icontains"],
        "manufacturer__id": ["exact"],
        "manufacturer__slug": ["exact", "in"],
        "color_name": ["exact", "icontains"],
        "published": ["exact"],
        "color_parent": ["exact", "icontains"],
        "alt_color_parent": ["exact", "icontains"],
        "filament_type__parent_type__name": ["exact", "icontains", "in"],
        "filament_type__parent_type__slug": ["exact", "in"],
    }
    throttle_classes = [BurstRateThrottle, SustainedRateThrottle]
    pagination_class = SmallPageNumberPagination

    def get_queryset(self, force_all=False):
        # `published` is set in the init
        kwargs = {} if force_all else {"replaced_by__isnull": True}
        queryset = Swatch.objects.filter(**kwargs).annotate(
            is_available=ExpressionWrapper(
                (
                    (
                        Q(amazon_purchase_link__isnull=False)
                        & ~Q(amazon_purchase_link="")
                    )
                    | (Q(mfr_purchase_link__isnull=False) & ~Q(mfr_purchase_link=""))
                ),
                output_field=BooleanField(),
            )
        )
        queryset = annotate_with_calculated_td(queryset)

        # Full-text search (q or f) across color_name, manufacturer.name, filament_type.name
        search = self.request.query_params.get("q") or self.request.query_params.get(
            "f"
        )
        if search and search != "null":
            for token in search.strip().lower().split():
                filters = (
                    Q(color_name__icontains=token)
                    | Q(manufacturer__name__icontains=token)
                    | Q(filament_type__name__icontains=token)
                )
                if token in ["grey", "gray"]:
                    filters = filters | Q(
                        color_name__icontains="grey" if token == "gray" else "gray"
                    )
                queryset = queryset.filter(filters)

        # Alias filters to match page routes without requiring frontend remap
        # mfr: manufacturer slug (alias)
        mfr = self.request.query_params.get("mfr")
        if mfr and mfr != "null":
            queryset = queryset.filter(manufacturer__slug=mfr)

        # ft: parent filament type (slug or id)
        ft = self.request.query_params.get("ft")
        if ft and ft != "null":
            try:
                # numeric id
                int(ft)
                queryset = queryset.filter(filament_type__parent_type__id=ft)
            except ValueError:
                queryset = queryset.filter(filament_type__parent_type__slug=ft)

        # cf: color family (slug or id) — matches either color_parent or alt_color_parent
        cf = self.request.query_params.get("cf")
        if cf and cf != "null":
            try:
                # Try to resolve via Swatch helper (accepts slug or id)
                f_id = Swatch().get_color_id_from_slug_or_id(cf)
            except Exception:
                f_id = None
            if f_id is not None:
                queryset = queryset.filter(
                    Q(color_parent=f_id) | Q(alt_color_parent=f_id)
                )

        # td: transmission distance range filter in the form "min-max"
        td = self.request.query_params.get("td")
        if td and td != "null":
            try:
                min_td, max_td = [float(x) for x in td.split("-")]
            except Exception:
                min_td, max_td = 0.0, 100.0
            queryset = queryset.filter(
                calculated_td__gte=min_td, calculated_td__lte=max_td
            )

        # Default ordering and basic server-side ordering options
        method = self.request.query_params.get("m")  # for method
        if method == "type":
            queryset = queryset.order_by("filament_type")
        elif method == "manufacturer":
            queryset = queryset.order_by("manufacturer")
        else:
            # Add a deterministic tie-breaker to avoid duplicates/gaps across pages
            queryset = queryset.order_by("-date_published", "-id")

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        method = request.query_params.get("m")

        if method in {"color", "random"}:
            items = list(queryset)
            if method == "color":
                items = sorted(items, key=get_hsv)
            else:  # random
                # Persist seed across the whole session for determinism, even if page=1 is re-requested
                seed = request.session.get("random_seed")
                if not seed:
                    seed = get_new_seed()
                    request.session["random_seed"] = seed
                rng = random.Random(seed)
                rng.shuffle(items)

            page_obj = self.paginate_queryset(items)
            if page_obj is not None:
                serializer = self.get_serializer(page_obj, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(items, many=True)
            return Response(serializer.data)

        # default behavior (type/manufacturer/date ordering handled in get_queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_queryset(force_all=True).filter(id=kwargs["pk"]).first()
        if not instance:
            return Response(status.HTTP_404_NOT_FOUND)
        while True:
            if instance.replaced_by:
                instance = instance.replaced_by
            else:
                break
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

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
            from colormath.color_conversions import convert_color

            results[color] = Swatch().get_closest_color_swatch(
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
