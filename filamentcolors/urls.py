"""filamentcolors URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps import GenericSitemap
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from filamentcolors import staff_views, views
from filamentcolors.api.urls import urlpatterns as api_urls
from filamentcolors.models import Swatch
from filamentcolors.sitemaps import StaticViewSitemap

handler400 = "filamentcolors.views.error_400"
handler404 = "filamentcolors.views.error_404"
handler500 = "filamentcolors.views.error_500"

sitemaps = {
    "static": StaticViewSitemap,
    "swatches": GenericSitemap(
        {
            "queryset": Swatch.objects.filter(published=True).order_by("id"),
            "date_field": "date_published",
        }
    ),
}

urlpatterns = [
    # Primary site URLs
    path("", views.homepage, name="homepage"),
    path("library/sort/<str:method>/", views.librarysort, name="librarysort"),
    path(
        "library/collection/edit/<str:ids>/",
        views.edit_swatch_collection,
        name="edit_collection",
    ),
    path(
        "library/collection/<str:ids>/",
        views.swatch_collection,
        name="swatchcollection",
    ),
    path("library/", views.librarysort, name="library"),
    path("swatch/<str:swatch_id>/", views.swatch_detail, name="swatchdetail"),
    path(
        "library/manufacturer/<str:mfr_id>/",
        views.manufacturersort,
        name="manufacturersort",
    ),
    path("library/manufacturer/", views.manufacturer_list, name="mfr_list"),
    path("library/filament_type/<int:id>/", views.typesort, name="typesort"),
    path(
        "library/color_family/<str:family_id>/",
        views.colorfamilysort,
        name="color_family_sort",
    ),
    path("donating/", views.donation_page, name="donations"),
    path("monetary_donating/", views.monetary_donation_page, name="monetary_donations"),
    path("inventory/", views.inventory_page, name="inventory"),
    path("about/", views.about_page, name="about"),
    path("colormatch/", views.colormatch, name="colormatch"),
    path(
        "single_swatch_card/<int:swatch_id>/",
        views.single_swatch_card,
        name="single_swatch_card",
    ),
    path(
        "welcome_experience_images/<int:image_id>/",
        views.get_welcome_experience_image,
        name="welcome_experience_image",
    ),
    path(
        "welcome_experience_video",
        views.get_welcome_experience_video,
        name="welcome_experience_video",
    ),
    path("visualizer/", views.swatch_field_visualizer, name="visualizer"),
    path("", include("plausible_proxy.urls")),
    # Admin urls
    path("admin/", admin.site.urls),
    path("logout/", staff_views.logout_view, name="logout"),
    path("add/swatch/", staff_views.add_swatch_landing, name="add_swatch_landing"),
    path(
        "add/swatch/inventory/<int:swatch_id>",
        staff_views.add_swatch,
        name="add_swatch_from_inventory",
    ),
    path("add/swatch/new/", staff_views.add_swatch, name="add_swatch"),
    path("add/manufacturer/", staff_views.add_manufacturer, name="add_mfr"),
    path("add/filamenttype/", staff_views.add_filament_type, name="add_filament_type"),
    path("add/inventory/", staff_views.add_inventory_swatch, name="add_inventory"),
    path("add/retailer/", staff_views.add_retailer, name="add_retailer"),
    path(
        "recalculate_color/<int:swatch_id>/",
        staff_views.recalculate_color,
        name="recalculate_color",
    ),
    path(
        "force_hex/<int:swatch_id>/",
        staff_views.force_hex_color,
        name="force_hex_color",
    ),
    path(
        "set_colors/",
        staff_views.set_colors_for_unpublished_swatches,
        name="set_colors",
    ),
    path(
        "update_images/<int:swatch_id>/",
        staff_views.update_swatch_images,
        name="update_images",
    ),
    path(
        "edit/<int:swatch_id>/purchase_locations/",
        staff_views.view_purchase_locations,
        name="view_purchase_locations",
    ),
    path(
        "edit/<int:swatch_id>/purchase_location/<int:location_id>",
        staff_views.edit_purchase_location,
        name="edit_purchase_location",
    ),
    path(
        "add/<int:swatch_id>/purchase_location/",
        staff_views.add_purchase_location,
        name="add_purchase_location",
    ),
    path(
        "edit/<int:swatch_id>/",
        staff_views.swatch_edit,
        name="edit_swatch",
    ),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("__debug__/", include("debug_toolbar.urls")),
    # Event / Special URLs
    # ...
    # Old links that need to exist for a while and just redirect.
    # Remove each of them after a reasonable amount of time has passed -- probably a few months.
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += api_urls
