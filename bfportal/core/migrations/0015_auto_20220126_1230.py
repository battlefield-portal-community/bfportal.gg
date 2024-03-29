# Generated by Django 3.2.11 on 2022-01-26 07:00

import modelcluster.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0014_experiencepage_categories"),
    ]

    operations = [
        migrations.AlterField(
            model_name="experiencepage",
            name="categories",
            field=modelcluster.fields.ParentalManyToManyField(
                blank=True,
                help_text="Choose from the Category",
                to="core.ExperiencesCategory",
            ),
        ),
        migrations.AlterField(
            model_name="experiencepage",
            name="code",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Six letter alpha-numeric code of you experience",
                max_length=6,
                verbose_name="Share Code",
            ),
        ),
        migrations.AlterField(
            model_name="experiencepage",
            name="cover_img_url",
            field=models.URLField(
                blank=True,
                default="",
                help_text="Link for your cover Image",
                verbose_name="Cover Image Url",
            ),
        ),
        migrations.AlterField(
            model_name="experiencepage",
            name="description",
            field=models.TextField(
                default="",
                help_text="Description of Your experience",
                verbose_name="Description",
            ),
        ),
        migrations.AlterField(
            model_name="experiencepage",
            name="exp_url",
            field=models.URLField(
                blank=True,
                default="",
                help_text="Url of your experience",
                verbose_name="Experience Url",
            ),
        ),
        migrations.AlterField(
            model_name="experiencepage",
            name="no_bots",
            field=models.PositiveIntegerField(
                blank=True,
                default=0,
                help_text="Max Number of Bots in your experience",
                verbose_name="Number Of Bots",
            ),
        ),
        migrations.AlterField(
            model_name="experiencepage",
            name="no_players",
            field=models.PositiveIntegerField(
                blank=True,
                default=0,
                help_text="Max Number of Human Players in your experience",
                verbose_name="Number of Human Players",
            ),
        ),
        migrations.AlterField(
            model_name="experiencepage",
            name="vid_url",
            field=models.URLField(
                blank=True,
                default="",
                help_text="Link to vid showcasing your experience",
                verbose_name="Video Url",
            ),
        ),
    ]
