# Generated by Django 3.2.12 on 2022-10-11 10:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0073_alter_discordscheduledevent_server_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="discordscheduledevent",
            name="event_id",
            field=models.IntegerField(
                help_text="ID of the event to show on website", null=True
            ),
        ),
        migrations.AlterField(
            model_name="discordscheduledevent",
            name="server_id",
            field=models.IntegerField(
                default=870246147455877181,
                help_text="ID of the server in which event is taking place [default: bfportal.gg discord server's id]",
                null=True,
            ),
        ),
    ]