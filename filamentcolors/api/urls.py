from django.urls import path, include, re_path
from rest_framework import routers

from filamentcolors.api.views import (
    FilamentTypeViewSet,
    ManufacturerViewSet,
    SwatchViewSet,
    db_version,
)

router = routers.DefaultRouter()

router.register(r"filament_type", FilamentTypeViewSet, basename="filament_type")
router.register(r"swatch", SwatchViewSet, basename="swatch")
router.register(r"manufacturer", ManufacturerViewSet, basename="manufacturer")

urlpatterns = [
    re_path(r"^api/", include(router.urls)),
    path("api/version/", db_version, name="db_version"),
]
