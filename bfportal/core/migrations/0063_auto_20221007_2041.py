# Generated by Django 3.2.12 on 2022-10-07 20:41

import modelcluster.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0062_auto_20221007_2022"),
    ]

    operations = [
        migrations.AddField(
            model_name="experiencepage",
            name="broken",
            field=models.BooleanField(
                default=False,
                help_text="Is the experience broken",
                verbose_name="Broken ?",
            ),
        ),
        migrations.AddField(
            model_name="experiencepage",
            name="broken_report",
            field=modelcluster.fields.ParentalManyToManyField(
                blank=True,
                help_text="People who have reported this is exp broken",
                related_name="broken_report",
                to="core.Profile",
            ),
        ),
        migrations.AddField(
            model_name="experiencepage",
            name="xp_farm",
            field=models.BooleanField(
                default=False,
                help_text="Is the experience an xp farm",
                verbose_name="Broken ?",
            ),
        ),
        migrations.AddField(
            model_name="experiencepage",
            name="xp_farm_report",
            field=modelcluster.fields.ParentalManyToManyField(
                blank=True,
                help_text="People who have reported this is exp an xp farm",
                related_name="xp_farm_report",
                to="core.Profile",
            ),
        ),
        migrations.AlterField(
            model_name="experiencepage",
            name="bugged_report",
            field=modelcluster.fields.ParentalManyToManyField(
                blank=True,
                help_text="People who have reported this exp is bugged",
                related_name="bugged_report",
                to="core.Profile",
            ),
        ),
    ]