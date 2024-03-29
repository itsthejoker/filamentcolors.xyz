from django.contrib import admin
from django.shortcuts import HttpResponseRedirect

from filamentcolors.models import (
    FilamentType,
    GenericFilamentType,
    GenericFile,
    Manufacturer,
    PurchaseLocation,
    Retailer,
    Swatch,
)


class SwatchAdmin(admin.ModelAdmin):
    list_display = ["color_name", "manufacturer", "filament_type", "published"]
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
        "closest_pantone_1",
        "closest_pantone_2",
        "closest_pantone_3",
        "closest_ral_1",
        "closest_ral_2",
        "closest_ral_3",
    )

    def response_change(self, request, obj):
        res = super().response_change(request, obj)
        if "_swatch_preview" in request.POST:
            return HttpResponseRedirect(f"/swatch/{obj.id}")
        else:
            return res


@admin.action(description="Recalculate affiliate links")
def recalculate_aff_links(modeladmin, request, queryset):
    s = Swatch.objects.filter(manufacturer__in=queryset.values_list("id", flat=True))
    for obj in s:
        obj.update_affiliate_links()
        obj.save()


class ManufacturerAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    ordering = ("name",)
    actions = [recalculate_aff_links]


class FilamentTypeAdmin(admin.ModelAdmin):
    ordering = ("name",)


admin.site.register(Swatch, SwatchAdmin)
admin.site.register(Manufacturer, ManufacturerAdmin)
admin.site.register(FilamentType, FilamentTypeAdmin)
admin.site.register(GenericFile)
admin.site.register(GenericFilamentType)
admin.site.register(Retailer)
admin.site.register(PurchaseLocation)
