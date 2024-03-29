# Generated by Django 3.2.12 on 2022-10-11 10:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0072_auto_20221011_1055"),
    ]

    operations = [
        migrations.AlterField(
            model_name="discordscheduledevent",
            name="server_id",
            field=models.CharField(
                default="870246147455877181",
                help_text="ID of the server in which event is taking place [default: bfportal.gg discord server's id]",
                max_length=255,
                null=True,
            ),
        ),
    ]
