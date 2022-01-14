from pyexpat import model
from django.db import models
from django.shortcuts import render

from wagtail.core.models import Page
from wagtail.admin.edit_handlers import FieldPanel

class IndexPage(Page):
    max_count = 1
    parent_page_types = ['wagtailcore.Page']

class ExperiencePage(Page):
    name = models.CharField(max_length=255, default='')
    code = models.CharField(max_length=6, default='')
    exp_url = models.URLField(default='')
    vid_url = models.URLField(default='')
    cover_img_url = models.URLField(default='')
    description = models.TextField(default='')
    no_players = models.IntegerField(default=-1)
    no_bots = models.IntegerField(default=-1)

    
    content_panels = Page.content_panels + [
        FieldPanel('name', classname='full'),
        FieldPanel('code', classname='full'),
        FieldPanel('exp_url', classname='full'),
        FieldPanel('description', classname='full'),
        FieldPanel('cover_img_url', classname='full'),
        FieldPanel('vid_url', classname='full'),
        FieldPanel('no_players', classname='full'),
        FieldPanel('no_bots', classname='full'),
    ]

    parent_page_types =  ['IndexPage']
