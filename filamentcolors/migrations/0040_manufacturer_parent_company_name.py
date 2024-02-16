# Generated by Django 5.0.2 on 2024-02-16 03:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("filamentcolors", "0039_delete_post"),
    ]

    operations = [
        migrations.AddField(
            model_name="manufacturer",
            name="parent_company_name",
            field=models.CharField(
                blank=True,
                help_text="Used for purchase buttons.",
                max_length=160,
                null=True,
            ),
        ),
    ]
