# Generated by Django 2.1.4 on 2019-04-20 04:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('filamentcolors', '0009_swatch_regenerate_info'),
    ]

    operations = [
        migrations.CreateModel(
            name='GenericFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='')),
            ],
        ),
    ]