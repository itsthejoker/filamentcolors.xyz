# Generated by Django 2.1.4 on 2019-02-24 02:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Printer",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=50)),
                ("notes", models.TextField(blank=True, max_length=4000, null=True)),
                ("image", models.ImageField(blank=True, null=True, upload_to="")),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Swatch",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("manufacturer", models.CharField(max_length=160)),
                ("color_name", models.CharField(max_length=240)),
                ("filament_type", models.CharField(default="PLA", max_length=10)),
                ("hot_end_temp", models.IntegerField(default=205)),
                ("bed_temp", models.IntegerField(default=60)),
                ("card_img_jpeg", models.ImageField(blank=True, upload_to="card_img")),
                ("card_img", models.ImageField(blank=True, upload_to="")),
                ("hex_color", models.CharField(blank=True, max_length=6)),
                ("complement_hex", models.CharField(blank=True, max_length=6)),
                ("image_back", models.ImageField(blank=True, null=True, upload_to="")),
                ("image_front", models.ImageField(blank=True, null=True, upload_to="")),
                ("image_other", models.ImageField(blank=True, null=True, upload_to="")),
                ("date_added", models.DateTimeField(default=django.utils.timezone.now)),
                ("notes", models.TextField(blank=True, max_length=4000, null=True)),
                ("purchase_link", models.URLField(blank=True, null=True)),
                (
                    "maker",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "printed_on",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="filamentcolors.Printer",
                    ),
                ),
            ],
        ),
    ]
