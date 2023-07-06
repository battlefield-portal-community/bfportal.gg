# Generated by Django 3.2.12 on 2022-09-19 17:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0049_experiencepage_allow_editing"),
    ]

    operations = [
        migrations.AddField(
            model_name="experiencescategory",
            name="selectable_on_form",
            field=models.BooleanField(
                default=True,
                help_text="Should this Category be selectable in submit form",
            ),
        ),
        migrations.AddField(
            model_name="subcategory",
            name="selectable_on_form",
            field=models.BooleanField(
                default=True,
                help_text="Should this Category be selectable in submit form",
            ),
        ),
    ]
