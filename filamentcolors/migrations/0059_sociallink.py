# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("filamentcolors", "0058_manufacturer_awin_affiliate_id"),
    ]

    operations = [
        migrations.CreateModel(
            name="SocialLink",
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
                ("name", models.CharField(max_length=100)),
                ("url", models.URLField(max_length=2000)),
                (
                    "order",
                    models.IntegerField(
                        default=0, help_text="Lower numbers will be shown first."
                    ),
                ),
                (
                    "active",
                    models.BooleanField(
                        default=True,
                        help_text="Whether this link should be shown on the links page.",
                    ),
                ),
            ],
            options={
                "ordering": ["order", "name"],
            },
        ),
    ]
