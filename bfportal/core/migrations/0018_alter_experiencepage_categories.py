# Generated by Django 3.2.11 on 2022-01-31 12:19

from django.db import migrations
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0017_auto_20220127_1533"),
    ]

    operations = [
        migrations.AlterField(
            model_name="experiencepage",
            name="categories",
            field=modelcluster.fields.ParentalManyToManyField(
                help_text="Choose from the Category", to="core.ExperiencesCategory"
            ),
        ),
    ]