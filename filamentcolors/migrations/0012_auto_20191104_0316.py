# Generated by Django 2.1.4 on 2019-11-04 03:16

from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ("taggit", "0003_taggeditem_add_unique_index"),
        ("filamentcolors", "0011_auto_20190515_0146"),
    ]

    operations = [
        migrations.CreateModel(
            name="GenericFilamentType",
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
                ("name", models.CharField(default="PLA", max_length=24)),
            ],
        ),
        migrations.AddField(
            model_name="swatch",
            name="color_parent",
            field=models.CharField(
                blank=True,
                choices=[
                    ("WHT", "White"),
                    ("BLK", "Black"),
                    ("RED", "Red"),
                    ("GRN", "Green"),
                    ("YLW", "Yellow"),
                    ("BLU", "Blue"),
                    ("BRN", "Brown"),
                    ("PPL", "Purple"),
                    ("PNK", "Pink"),
                    ("RNG", "Orange"),
                    ("GRY", "Grey"),
                ],
                default="WHT",
                max_length=3,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="swatch",
            name="tags",
            field=taggit.managers.TaggableManager(
                help_text="A comma-separated list of tags.",
                through="taggit.TaggedItem",
                to="taggit.Tag",
                verbose_name="Tags",
            ),
        ),
        migrations.AlterField(
            model_name="swatch",
            name="analogous_1",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="analogous_one_swatch",
                to="filamentcolors.Swatch",
            ),
        ),
        migrations.AlterField(
            model_name="swatch",
            name="analogous_2",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="analogous_two_swatch",
                to="filamentcolors.Swatch",
            ),
        ),
        migrations.AlterField(
            model_name="swatch",
            name="complement",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="complement_swatch",
                to="filamentcolors.Swatch",
            ),
        ),
        migrations.AlterField(
            model_name="swatch",
            name="split_complement_1",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="split_complement_one_swatch",
                to="filamentcolors.Swatch",
            ),
        ),
        migrations.AlterField(
            model_name="swatch",
            name="split_complement_2",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="split_complement_two_swatch",
                to="filamentcolors.Swatch",
            ),
        ),
        migrations.AlterField(
            model_name="swatch",
            name="square_1",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="square_one_swatch",
                to="filamentcolors.Swatch",
            ),
        ),
        migrations.AlterField(
            model_name="swatch",
            name="square_2",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="square_two_swatch",
                to="filamentcolors.Swatch",
            ),
        ),
        migrations.AlterField(
            model_name="swatch",
            name="square_3",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="square_three_swatch",
                to="filamentcolors.Swatch",
            ),
        ),
        migrations.AlterField(
            model_name="swatch",
            name="tetradic_1",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="tetradic_one_swatch",
                to="filamentcolors.Swatch",
            ),
        ),
        migrations.AlterField(
            model_name="swatch",
            name="tetradic_2",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="tetradic_two_swatch",
                to="filamentcolors.Swatch",
            ),
        ),
        migrations.AlterField(
            model_name="swatch",
            name="tetradic_3",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="tetradic_three_swatch",
                to="filamentcolors.Swatch",
            ),
        ),
        migrations.AlterField(
            model_name="swatch",
            name="triadic_1",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="triadic_one_swatch",
                to="filamentcolors.Swatch",
            ),
        ),
        migrations.AlterField(
            model_name="swatch",
            name="triadic_2",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="triadic_two_swatch",
                to="filamentcolors.Swatch",
            ),
        ),
        migrations.AddField(
            model_name="filamenttype",
            name="parent_type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to="filamentcolors.GenericFilamentType",
            ),
        ),
    ]
