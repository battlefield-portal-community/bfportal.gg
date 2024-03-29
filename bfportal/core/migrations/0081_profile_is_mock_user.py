# Generated by Django 4.1.7 on 2023-07-07 15:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0080_alter_experiencepagetag_tag"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="is_mock_user",
            field=models.BooleanField(
                default=False,
                help_text="If set to true, this user was created by the mock command, and is a fake user",
            ),
        ),
    ]
