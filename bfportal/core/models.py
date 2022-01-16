from django.db import models
from django.template.response import TemplateResponse
from django.shortcuts import render

from wagtail.core.models import Page
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route

from allauth.socialaccount.models import SocialAccount

class IndexPage(RoutablePageMixin, Page):
    max_count = 1
    parent_page_types = ['wagtailcore.Page']
    subpage_types = ['core.ExperiencePage']

    @route(r'^$')
    def base(self, request):
        return TemplateResponse(
            request,
            self.get_template(request),
            self.get_context(request)
        )
    
    @route(r'^submit/$')
    def submit_exp(self, request):
        from core.views import sumbit_experience
        return sumbit_experience(request, self)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        if request.user.is_authenticated:
            context['social_user'] = SocialAccount.objects.get(user=request.user)
        return context


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
