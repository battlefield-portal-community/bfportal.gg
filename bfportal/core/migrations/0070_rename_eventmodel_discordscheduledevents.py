# Generated by Django 3.2.12 on 2022-10-11 10:51

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0069_auto_20221011_1050"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="EventModel",
            new_name="DiscordScheduledEvents",
        ),
    ]
