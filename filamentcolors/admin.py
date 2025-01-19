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
    UserSubmittedTD,
    DeadLink,
)


class UserSubmittedTDAdmin(admin.ModelAdmin):
    ordering = ("swatch__color_name", "swatch__manufacturer__name")
    search_fields = ("swatch__color_name",)


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


@admin.action(description="Recalculate Affiliate Links")
def recalculate_aff_links(modeladmin, request, queryset):
    s = Swatch.objects.filter(manufacturer__in=queryset.values_list("id", flat=True))
    for obj in s:
        obj.update_affiliate_links()
        obj.save()


@admin.action(description="Remove Purchase Links")
def remove_purchase_links(modeladmin, request, queryset):
    # todo: make this also work for retailer links
    s = Swatch.objects.filter(manufacturer__in=queryset.values_list("id", flat=True))
    for obj in s:
        obj.amazon_purchase_link = None
        obj.mfr_purchase_link = None
        obj.save()


class ManufacturerAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    ordering = ("name",)
    actions = [recalculate_aff_links, remove_purchase_links]


class FilamentTypeAdmin(admin.ModelAdmin):
    ordering = ("name",)


class DeadLinkAdmin(admin.ModelAdmin):
    readonly_fields = ("swatch",)

    def response_change(self, request, obj):
        res = super().response_change(request, obj)
        if "_apply_deadlink_suggestion" in request.POST:
            if obj.link_type == "mfr":
                obj.swatch.mfr_purchase_link = obj.suggested_url
            elif obj.link_type == "amazon":
                obj.swatch.amazon_purchase_link = obj.suggested_url
            obj.swatch.save()
            obj.delete()
            return res
        else:
            return res


admin.site.register(Swatch, SwatchAdmin)
admin.site.register(Manufacturer, ManufacturerAdmin)
admin.site.register(FilamentType, FilamentTypeAdmin)
admin.site.register(UserSubmittedTD, UserSubmittedTDAdmin)
admin.site.register(GenericFile)
admin.site.register(GenericFilamentType)
admin.site.register(Retailer)
admin.site.register(PurchaseLocation)
admin.site.register(DeadLink, DeadLinkAdmin)
