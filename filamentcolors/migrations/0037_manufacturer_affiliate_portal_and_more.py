# Generated by Django 5.0 on 2024-01-18 02:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("filamentcolors", "0036_alter_manufacturer_swap_purchase_buttons"),
    ]

    operations = [
        migrations.AddField(
            model_name="manufacturer",
            name="affiliate_portal",
            field=models.CharField(blank=True, max_length=2000, null=True),
        ),
        migrations.AddField(
            model_name="manufacturer",
            name="affiliate_url_param",
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
