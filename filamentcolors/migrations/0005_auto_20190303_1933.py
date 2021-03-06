# Generated by Django 2.1.4 on 2019-03-03 19:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("filamentcolors", "0004_filamenttype_manufacturer"),
    ]

    operations = [
        migrations.AddField(
            model_name="swatch",
            name="filament_type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="filamentcolors.FilamentType",
            ),
        ),
        migrations.AddField(
            model_name="swatch",
            name="manufacturer",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="filamentcolors.Manufacturer",
            ),
        ),
    ]
