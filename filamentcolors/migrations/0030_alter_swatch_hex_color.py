# Generated by Django 4.1.2 on 2022-11-28 05:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("filamentcolors", "0029_alter_filamenttype_parent_type_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="swatch",
            name="hex_color",
            field=models.CharField(
                blank=True, max_length=6, verbose_name="Measured hex value"
            ),
        ),
    ]