from django.db import models
from django.template.response import TemplateResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from wagtail.core.models import Page
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route

from taggit.models import TaggedItemBase

from modelcluster.models import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager

from allauth.socialaccount.models import SocialAccount

from loguru import logger

from bfportal.settings.base import LOGIN_URL


class HomePage(RoutablePageMixin, Page):
    max_count = 1
    parent_page_types = ['wagtailcore.Page']
    subpage_types = ['core.ExperiencesPage', 'core.ProfilePage']

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
        context['posts'] = ExperiencePage.objects.live().public().order_by('-first_published_at')
        return context


class ExperiencePageTag(TaggedItemBase):
    content_object  = ParentalKey(
        'ExperiencePage',
        related_name='tagged_items',
        on_delete=models.CASCADE,
    )


class ExperiencesPage(RoutablePageMixin, Page):
    max_count = 1
    parent_page_types = ['core.HomePage']
    subpage_types = ['core.ExperiencePage']

    def get_context(self, request, *args, **kwargs):
        """Adding custom stuff to our context."""
        context = super().get_context(request, *args, **kwargs)
        # Get all posts
        all_posts = ExperiencePage.objects.live().public().order_by('-first_published_at')

        if request.GET.get('tag', None):
            tags = request.GET.get('tag')
            all_posts = all_posts.filter(tags__slug__in=[tags])
            logger.debug(f"Filted {len(all_posts)} experiences by tags {tags}")

        context["posts"] = all_posts
        return context


class ExperiencePage(RoutablePageMixin ,Page):
    description = models.TextField(default='', help_text="Description of Your experience")

    code = models.CharField(blank=True, max_length=6, default='', help_text="Six letter alpha-numeric code of you experience")
    exp_url = models.URLField(blank=True, default='', help_text="Url of your experience")
    
    tags = ClusterTaggableManager(blank=True, help_text="Some tags", through=ExperiencePageTag)
    vid_url = models.URLField(blank=True, default='', help_text="Link to vid showcasing your experience")
    cover_img_url = models.URLField(blank=True, default='', help_text="Link for your cover Image")
    
    no_players = models.IntegerField(blank=True, default=-1, help_text="Max Number of Human Players in your experience")
    no_bots = models.IntegerField(blank=True, default=-1, help_text="Max Number of Bots in your experience")

    
    content_panels = Page.content_panels + [
        FieldPanel('description', classname='full'),

        FieldPanel('code', classname='full'),
        FieldPanel('exp_url', classname='full'),

        FieldPanel('tags'),
        FieldPanel('cover_img_url', classname='full'),
        FieldPanel('vid_url', classname='full'),

        FieldPanel('no_players', classname='full'),
        FieldPanel('no_bots', classname='full'),
    ]

    parent_page_types =  ['core.ExperiencesPage']
    subpage_types = []

    @route(r'^edit/$')
    def edit_page(self, request):
        if request.user.is_authenticated and self.owner == request.user:
            from .views import edit_experience
            return edit_experience(request, self)
        else:
            return redirect(LOGIN_URL)

class ProfilePage(RoutablePageMixin, Page):

    max_count = 1
    parent_page_types = ['core.HomePage']
    subpage_types = []


    def serve(self, request, view=None, args=None, kwargs=None):
        if request.user.is_authenticated:
            return super().serve(request, view, args, kwargs)
        else:
            return redirect(LOGIN_URL)

    def get_context(self, request, *args, **kwargs):
        l = kwargs.pop('list_experiences', None)
        context = super().get_context(request, *args, **kwargs)
        if l:
            posts = ExperiencePage.objects.live().public().filter(owner=request.user)
            logger.debug(f"filtred {len(posts)} for {request.user}")
            context['posts'] = posts

        return context


    @route(r'experiences/$')
    def user_experiences(self, request):
        return TemplateResponse(
            request,
            "core/experiences_page.html",
            self.get_context(request, list_experiences=True),
        )