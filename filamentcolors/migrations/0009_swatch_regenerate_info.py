# Generated by Django 2.1.4 on 2019-03-24 01:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("filamentcolors", "0008_auto_20190323_2357"),
    ]

    operations = [
        migrations.AddField(
            model_name="swatch",
            name="regenerate_info",
            field=models.BooleanField(default=False),
        ),
    ]
