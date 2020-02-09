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
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from filamentcolors import views
from filamentcolors.api.urls import urlpatterns as api_urls

# Django magic
handler404 = 'filamentcolors.views.handler404'
handler500 = 'filamentcolors.views.handler500'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.homepage, name='homepage'),
    path('library/sort/<str:method>/', views.librarysort, name='librarysort'),
    path('library/collection/edit/<str:ids>/', views.edit_swatch_collection, name='edit_collection'),
    path('library/collection/<str:ids>/', views.swatch_collection, name='swatchcollection'),
    path('library/', views.librarysort, name='library'),
    path('swatch/<int:id>', views.swatch_detail, name='swatchdetail'),
    path('library/manufacturer/<int:id>', views.manufacturersort, name='manufacturersort'),
    path('library/filament_type/<int:id>', views.typesort, name='typesort'),
    path('library/color_family/<str:family_id>', views.colorfamilysort, name='color_family_sort'),
    # path('printer/<int:id>', views.printer_detail, name='printerdetail'),
    path('about/', views.about_page, name='about'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += api_urls
