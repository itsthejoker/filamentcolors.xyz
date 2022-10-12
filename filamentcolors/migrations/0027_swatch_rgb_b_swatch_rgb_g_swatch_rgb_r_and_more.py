# Generated by Django 4.1.1 on 2022-10-12 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "filamentcolors",
            "0026_swatch_closest_pantone_1_swatch_closest_pantone_2_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="swatch",
            name="rgb_b",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="swatch",
            name="rgb_g",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="swatch",
            name="rgb_r",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="manufacturer",
            name="website",
            field=models.URLField(blank=True, max_length=2000, null=True),
        ),
        migrations.AlterField(
            model_name="swatch",
            name="amazon_purchase_link",
            field=models.URLField(blank=True, max_length=2000, null=True),
        ),
        migrations.AlterField(
            model_name="swatch",
            name="mfr_purchase_link",
            field=models.URLField(blank=True, max_length=2000, null=True),
        ),
    ]
