# Generated by Django 5.1.4 on 2025-01-20 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("filamentcolors", "0052_swatch_lab_a_swatch_lab_b_swatch_lab_l"),
    ]

    operations = [
        migrations.AddField(
            model_name="swatch",
            name="computed_lab",
            field=models.BooleanField(default=False),
        ),
    ]
