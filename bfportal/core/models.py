from typing import Union

from django.db import models
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse
from django.shortcuts import render, redirect

from wagtail.core.models import Page
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.snippets.models import register_snippet

from allauth.socialaccount.templatetags.socialaccount import get_social_accounts
from allauth.socialaccount.models import SocialAccount
from taggit.models import TaggedItemBase

from modelcluster.models import ParentalKey, ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager

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
        from core.views import submit_experience
        return submit_experience(request, self)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context['posts'] = ExperiencePage.objects.live().public().order_by('-first_published_at')
        return context


class ExperiencesCategory(models.Model):
    name = models.CharField(max_length=255)
    icon = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+'
    )

    panels = [
        FieldPanel('name'),
        ImageChooserPanel('icon'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'experiences categories'


register_snippet(ExperiencesCategory)


class ExperiencePageTag(TaggedItemBase):
    content_object = ParentalKey(
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
        logger.debug([cat.name for cat in all_posts[0].categories.all()])
        if tags := request.GET.get('tag', None):
            all_posts = all_posts.filter(tags__slug__in=[tags])
            logger.debug(f"Filted {len(all_posts)} experiences by tags {tags}")
        elif category := request.GET.get('category', None):
            all_posts = [
                post for post in all_posts
                if category.lower() in [cat.name.lower() for cat in post.categories.all()]
            ]

        context["posts"] = all_posts
        return context


class ExperiencePage(RoutablePageMixin, Page):
    description = models.TextField(default='', help_text="Description of Your experience")

    code = models.CharField(blank=True, max_length=6, default='',
                            help_text="Six letter alpha-numeric code of you experience")
    exp_url = models.URLField(blank=True, default='', help_text="Url of your experience")

    tags = ClusterTaggableManager(blank=True, help_text="Some tags", through=ExperiencePageTag)
    vid_url = models.URLField(blank=True, default='', help_text="Link to vid showcasing your experience")
    cover_img_url = models.URLField(blank=True, default='', help_text="Link for your cover Image")

    no_players = models.IntegerField(blank=True, default=-1, help_text="Max Number of Human Players in your experience")
    no_bots = models.IntegerField(blank=True, default=-1, help_text="Max Number of Bots in your experience")
    categories = ParentalManyToManyField('core.ExperiencesCategory', blank=True)

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('description', classname='full'),
            FieldPanel('categories', widget=forms.CheckboxSelectMultiple)
        ], heading="Basic Info", classname="collapsible"),

        MultiFieldPanel([
            FieldPanel('code', classname='full'),
            FieldPanel('exp_url', classname='full')
        ], heading="Sharing Info", classname="collapsible"),

        MultiFieldPanel([
            FieldPanel('tags'),
            FieldPanel('cover_img_url', classname='full'),
            FieldPanel('vid_url', classname='full'),
        ], heading="Extra Info", classname="collapsible"),

        MultiFieldPanel([
            FieldPanel('no_players', classname='full'),
            FieldPanel('no_bots', classname='full'),
        ], heading="Settings info", classname="collapsible"),
    ]

    parent_page_types = ['core.ExperiencesPage']
    subpage_types = []

    @route(r'^edit/$')
    def edit_page(self, request: HttpRequest):
        if request.user.is_authenticated:
            if self.owner == request.user:
                from .views import edit_experience
                return edit_experience(request, self)
            else:
                logger.debug(f"{request.user} tried to edit a experience they dont own exp: {request.path}")
                return HttpResponse("Unauthorized", status=401)
        else:
            return redirect(LOGIN_URL)


def social_user(discord_id: int):
    """Returns a User object for a discord id"""
    try:
        return get_user_model().objects.get(id=SocialAccount.objects.get(uid=discord_id).user_id)
    except ObjectDoesNotExist:
        return False


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
        user_acc = kwargs.pop('user', None)
        context = super().get_context(request, *args, **kwargs)
        if not user_acc:
            user_acc = request.user
        if l:
            posts = ExperiencePage.objects.live().public().filter(owner=user_acc)
            logger.debug(f"filtred {len(posts)} for {user_acc}")
            context['posts'] = posts
        return context

    @route(r"^$")
    def root_profile_page(self, request):
        return redirect("/")

    @route(r"^(\d{18})/$", name='discord_id')
    def profile_page_view(self, request: HttpRequest, discord_id):
        user = social_user(discord_id)
        if user:
            return TemplateResponse(
                request,
                self.get_template(request),
                {"user": user}
            )
        else:
            return HttpResponse("Nope", status=404)

    @route(r'(\d{18})/experiences/$', name='discord_id')
    def user_experiences(self, request, discord_id):
        user = social_user(discord_id=discord_id)
        if user:
            return TemplateResponse(
                request,
                "core/experiences_page.html",
                self.get_context(request=request, list_experiences=True, user=user)
            )
        else:
            return HttpResponse("User not Found", status=404)
