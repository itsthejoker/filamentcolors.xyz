# Generated by Django 5.0.2 on 2024-02-26 03:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("filamentcolors", "0041_retailer_purchaselocation"),
    ]

    operations = [
        migrations.CreateModel(
            name="PantonePMS",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("code", models.CharField(max_length=48)),
                ("rgb_r", models.IntegerField()),
                ("rgb_g", models.IntegerField()),
                ("rgb_b", models.IntegerField()),
                ("hex_color", models.CharField(blank=True, max_length=6, null=True)),
            ],
        ),
    ]
