from django.contrib import admin
from django.shortcuts import HttpResponseRedirect

from filamentcolors.models import FilamentType
from filamentcolors.models import GenericFilamentType
from filamentcolors.models import GenericFile
from filamentcolors.models import Manufacturer
from filamentcolors.models import Printer
from filamentcolors.models import Swatch


class SwatchAdmin(admin.ModelAdmin):
    ordering = ('manufacturer__name',)
    search_fields = ['color_name', 'manufacturer__name']
    exclude = (
        'complement',
        'analogous_1',
        'analogous_2',
        'triadic_1',
        'triadic_2',
        'split_complement_1',
        'split_complement_2',
        'tetradic_1',
        'tetradic_2',
        'tetradic_3',
        'square_1',
        'square_2',
        'square_3',
    )

    def response_change(self, request, obj):
        res = super().response_change(request, obj)
        if "_preview" in request.POST:
            return HttpResponseRedirect(f'/swatch/{obj.id}')
        else:
            return res


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
admin.site.register(GenericFile)
admin.site.register(GenericFilamentType)
