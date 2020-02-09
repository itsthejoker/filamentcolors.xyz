from filamentcolors.api.views import FilamentTypeViewSet, SwatchViewSet, ManufacturerViewSet
from django.conf.urls import include, url

from rest_framework import routers

router = routers.DefaultRouter()

router.register(r'filament_type', FilamentTypeViewSet, basename='filament_type')
router.register(r'swatch', SwatchViewSet, basename='swatch')
router.register(r'manufacturer', ManufacturerViewSet, basename='manufacturer')

urlpatterns = [
    url(r"^api/", include(router.urls)),
]