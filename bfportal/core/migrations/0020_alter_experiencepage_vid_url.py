# Generated by Django 3.2.11 on 2022-02-13 17:52

import embed_video.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_availabletags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experiencepage',
            name='vid_url',
            field=embed_video.fields.EmbedVideoField(blank=True, default='', help_text='Link to vid showcasing your experience', verbose_name='Video Url'),
        ),
    ]
