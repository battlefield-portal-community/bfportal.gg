# Generated by Django 3.2.12 on 2022-08-24 14:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0031_alter_experiencepage_cover_img_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="experiencepage",
            name="bugged",
            field=models.BooleanField(
                default=False,
                help_text="Is the experience bugged",
                verbose_name="Bugged ?",
            ),
        ),
    ]
