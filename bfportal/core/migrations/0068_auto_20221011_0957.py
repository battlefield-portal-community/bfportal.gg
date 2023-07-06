# Generated by Django 3.2.12 on 2022-10-11 09:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0067_auto_20221011_0950"),
    ]

    operations = [
        migrations.AddField(
            model_name="eventmodel",
            name="event_link",
            field=models.URLField(blank=True, help_text="URL of the event", null=True),
        ),
        migrations.AddField(
            model_name="eventmodel",
            name="name",
            field=models.CharField(
                blank=True,
                help_text="Name of the event (only for admin panel)",
                max_length=255,
                null=True,
            ),
        ),
    ]
