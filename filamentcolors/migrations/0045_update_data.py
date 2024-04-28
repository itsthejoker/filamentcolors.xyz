from django.db import migrations
from django.template.defaultfilters import slugify


def update_models(apps, schema_editor):
    # django migrations don't run the overridden .save() method, so we need to manually call it
    for manufacturer in apps.get_model("filamentcolors", "Manufacturer").objects.all():
        manufacturer.slug = slugify(
            manufacturer.parent_company_name
            if manufacturer.parent_company_name
            else manufacturer.name
        )
        manufacturer.save()

    for filament_type in apps.get_model(
        "filamentcolors", "GenericFilamentType"
    ).objects.all():
        filament_type.slug = slugify(filament_type.name)
        filament_type.save()

    for swatch in apps.get_model("filamentcolors", "Swatch").objects.all():
        swatch.slug = slugify(
            f"{swatch.manufacturer.slug} {swatch.color_name}"
            f" {swatch.filament_type.name} {swatch.id}"
        )
        swatch.save()


class Migration(migrations.Migration):

    dependencies = [
        (
            "filamentcolors",
            "0044_genericfilamenttype_slug_manufacturer_slug_and_more",
        ),
    ]

    operations = [
        migrations.RunPython(update_models, migrations.RunPython.noop),
    ]
