# Generated by Django 3.2.12 on 2022-08-24 16:33

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0032_experiencepage_bugged"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="experiencescategory",
            name="bg_color",
        ),
        migrations.RemoveField(
            model_name="experiencescategory",
            name="bg_hover_color",
        ),
        migrations.RemoveField(
            model_name="experiencescategory",
            name="text_color",
        ),
        migrations.RemoveField(
            model_name="experiencescategory",
            name="text_hover_color",
        ),
    ]
