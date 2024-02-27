# Generated by Django 5.0.2 on 2024-02-26 04:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("filamentcolors", "0042_pantonepms"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="swatch",
            name="complement_hex",
        ),
        migrations.AddField(
            model_name="swatch",
            name="closest_pms_1",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="pms_1",
                to="filamentcolors.pantonepms",
                verbose_name="Computed Pantone PMS color 1",
            ),
        ),
        migrations.AddField(
            model_name="swatch",
            name="closest_pms_2",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="pms_2",
                to="filamentcolors.pantonepms",
                verbose_name="Computed Pantone PMS color 2",
            ),
        ),
        migrations.AddField(
            model_name="swatch",
            name="closest_pms_3",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="pms_3",
                to="filamentcolors.pantonepms",
                verbose_name="Computed Pantone PMS color 3",
            ),
        ),
    ]
