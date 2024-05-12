# Generated by Django 5.0.4 on 2024-05-12 05:19

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("filamentcolors", "0045_update_data"),
    ]

    operations = [
        migrations.AddField(
            model_name="swatch",
            name="td",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name="UserSubmittedTD",
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
                ("td", models.FloatField()),
                ("date_added", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "swatch",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="filamentcolors.swatch",
                    ),
                ),
            ],
        ),
    ]
