# Generated by Django 3.0.4 on 2020-07-22 00:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('filamentcolors', '0020_post'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='enable_preview',
            field=models.BooleanField(default=False),
        ),
    ]