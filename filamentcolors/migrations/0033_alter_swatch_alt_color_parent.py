# Generated by Django 4.1.5 on 2023-01-15 20:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("filamentcolors", "0032_swatch_alt_color_parent"),
    ]

    operations = [
        migrations.AlterField(
            model_name="swatch",
            name="alt_color_parent",
            field=models.CharField(
                blank=True,
                choices=[
                    ("WHT", "White"),
                    ("BLK", "Black"),
                    ("RED", "Red"),
                    ("GRN", "Green"),
                    ("YLW", "Yellow"),
                    ("BLU", "Blue"),
                    ("BRN", "Brown"),
                    ("PPL", "Purple"),
                    ("PNK", "Pink"),
                    ("RNG", "Orange"),
                    ("GRY", "Grey"),
                    ("TRN", "Translucent"),
                ],
                max_length=3,
                null=True,
            ),
        ),
    ]