# Generated by Django 3.2.12 on 2022-10-07 20:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0060_auto_20221004_1239"),
    ]

    operations = [
        migrations.AddField(
            model_name="experiencepage",
            name="bugged_report",
            field=models.ForeignKey(
                blank=True,
                help_text="People who have reported this exp bugged",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="core.profile",
            ),
        ),
    ]
