# Generated by Django 3.2.12 on 2022-09-20 10:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0050_auto_20220919_1727"),
    ]

    operations = [
        migrations.DeleteModel(
            name="AvailableTags",
        ),
    ]