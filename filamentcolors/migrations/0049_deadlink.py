# Generated by Django 5.0.6 on 2024-05-25 21:22

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("filamentcolors", "0048_usersubmittedtd_ip"),
    ]

    operations = [
        migrations.CreateModel(
            name="DeadLink",
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
                ("current_url", models.URLField(max_length=2000)),
                (
                    "suggested_url",
                    models.URLField(blank=True, max_length=2000, null=True),
                ),
                (
                    "link_type",
                    models.CharField(
                        choices=[
                            ("mfr", "Manufacturer"),
                            ("amazon", "Amazon"),
                            ("retailer", "Retailer"),
                        ],
                        max_length=10,
                    ),
                ),
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