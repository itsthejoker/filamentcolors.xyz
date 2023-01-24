# Generated by Django 4.1.5 on 2023-01-15 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("filamentcolors", "0031_swatch_date_published"),
    ]

    operations = [
        migrations.AddField(
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
                help_text="If a swatch looks like a combination of two base colors, set the second one here.",
                max_length=3,
                null=True,
            ),
        ),
    ]