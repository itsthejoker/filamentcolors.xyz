from django.contrib import admin
from django.db import models
from django.shortcuts import HttpResponseRedirect
from martor.widgets import AdminMartorWidget

from filamentcolors.models import (
    FilamentType,
    GenericFilamentType,
    GenericFile,
    Manufacturer,
    Swatch,
    Post,
)


class SwatchAdmin(admin.ModelAdmin):
    ordering = ("manufacturer__name",)
    search_fields = ["color_name", "manufacturer__name"]
    exclude = (
        "complement",
        "analogous_1",
        "analogous_2",
        "triadic_1",
        "triadic_2",
        "split_complement_1",
        "split_complement_2",
        "tetradic_1",
        "tetradic_2",
        "tetradic_3",
        "square_1",
        "square_2",
        "square_3",
        "closest_1",
        "closest_2",
    )

    def response_change(self, request, obj):
        res = super().response_change(request, obj)
        if "_swatch_preview" in request.POST:
            return HttpResponseRedirect(f"/swatch/{obj.id}")
        else:
            return res


class ManufacturerAdmin(admin.ModelAdmin):
    ordering = ("name",)


class FilamentTypeAdmin(admin.ModelAdmin):
    ordering = ("name",)


class PostAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {"widget": AdminMartorWidget},
    }

    def response_change(self, request, obj):
        res = super().response_change(request, obj)
        if "_post_preview" in request.POST:
            return HttpResponseRedirect(
                f"/post/{obj.slug}{'/preview/' if obj.enable_preview else ''}"
            )
        else:
            return res


admin.site.register(Swatch, SwatchAdmin)
admin.site.register(Manufacturer, ManufacturerAdmin)
admin.site.register(FilamentType, FilamentTypeAdmin)
admin.site.register(GenericFile)
admin.site.register(GenericFilamentType)
admin.site.register(Post, PostAdmin)
