from django.contrib import admin

from filamentcolors.models import FilamentType
from filamentcolors.models import Manufacturer
from filamentcolors.models import Printer
from filamentcolors.models import Swatch


class SwatchAdmin(admin.ModelAdmin):
    ordering = ('manufacturer__name',)


class PrinterAdmin(admin.ModelAdmin):
    ordering = ('name',)


class ManufacturerAdmin(admin.ModelAdmin):
    ordering = ('name',)


class FilamentTypeAdmin(admin.ModelAdmin):
    ordering = ('name',)


admin.site.register(Swatch, SwatchAdmin)
admin.site.register(Printer, PrinterAdmin)
admin.site.register(Manufacturer, ManufacturerAdmin)
admin.site.register(FilamentType, FilamentTypeAdmin)

