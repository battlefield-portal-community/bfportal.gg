# Generated by Django 3.2.12 on 2022-08-24 16:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0034_auto_20220824_1647"),
    ]

    operations = [
        migrations.AlterField(
            model_name="experiencepage",
            name="category",
            field=models.ForeignKey(
                help_text="Choose Main Category",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="core.experiencescategory",
            ),
        ),
    ]
