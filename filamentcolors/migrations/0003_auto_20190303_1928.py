# Generated by Django 2.1.4 on 2019-03-03 19:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("filamentcolors", "0002_auto_20190303_1851"),
    ]

    operations = [
        migrations.RenameField(
            model_name="swatch",
            old_name="bed_temp",
            new_name="bed_temp_str",
        ),
        migrations.RenameField(
            model_name="swatch",
            old_name="filament_type",
            new_name="filament_type_str",
        ),
        migrations.RenameField(
            model_name="swatch",
            old_name="hot_end_temp",
            new_name="hot_end_temp_str",
        ),
        migrations.RenameField(
            model_name="swatch",
            old_name="manufacturer",
            new_name="manufacturer_str",
        ),
    ]
