# Generated by Django 3.2.11 on 2022-01-31 12:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0018_alter_experiencepage_categories"),
    ]

    operations = [
        migrations.CreateModel(
            name="AvailableTags",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "tags",
                    models.TextField(
                        blank=True,
                        verbose_name="All available tags in BF 2042 Portal Rules editor",
                    ),
                ),
            ],
        ),
    ]
