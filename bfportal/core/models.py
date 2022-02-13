from typing import Union

from django.db import models
from django import forms
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse
from django.shortcuts import render, redirect

from wagtail.core.models import Page
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.snippets.models import register_snippet

from allauth.socialaccount.models import SocialAccount
from taggit.models import TaggedItemBase

from modelcluster.models import ParentalKey, ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager
from wagtail_color_panel.fields import ColorField
from wagtail_color_panel.edit_handlers import NativeColorPanel

from loguru import logger
from embed_video.fields import EmbedVideoField

from bfportal.settings.base import LOGIN_URL
from core.utils.helper import safe_cast


def pagination_wrapper(request: HttpRequest, posts: models.query.QuerySet) -> Paginator:
    paginator = Paginator(
        filter_tags_category(request, posts), request.GET.get("n", 10)
    )
    curr_page = safe_cast(request.GET.get("page", None), int, 1)
    try:
        # If the page exists and the ?page=x is an int
        posts = paginator.page(curr_page)
    except PageNotAnInteger:
        # If the ?page=x is not an int; show the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If the ?page=x is out of range (too high most likely)
        # Then return the last page
        posts = paginator.page(paginator.num_pages)

    return posts


def filter_tags_category(request: HttpRequest, posts: models.query.QuerySet):
    all_posts = posts
    if tags := request.GET.getlist("tag", None):
        all_posts = all_posts.filter(tags__slug__in=tags)
    if category := request.GET.getlist("category", None):
        category = list(map(str.lower, category))
        logger.debug(category)
        post: ExperiencePage
        all_posts = [
            post
            for post in all_posts
            if any(i in category for i in [cat.name.lower() for cat in post.categories.all()])
        ]

    if tags or category:
        logger.debug(
            f"filtered {len(all_posts)} experiences for tags {tags}, cat [{category}]"
        )
    return all_posts


class HomePage(RoutablePageMixin, Page):
    max_count = 1
    parent_page_types = ["wagtailcore.Page"]
    subpage_types = ["core.ExperiencesPage", "core.ProfilePage"]

    @route(r"^$")
    def base(self, request):
        return TemplateResponse(
            request, self.get_template(request), self.get_context(request)
        )

    @route(r"^submit/$")
    def submit_exp(self, request):
        from core.views import submit_experience

        return submit_experience(request, self)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        posts = pagination_wrapper(
            request,
            ExperiencePage.objects.live().public().order_by("-first_published_at"),
        )

        context["posts"] = posts
        return context


class ExperiencesCategory(models.Model):
    name = models.CharField(max_length=255)
    bg_color = ColorField(default="#474c50")
    bg_hover_color = ColorField(default="#474c50")
    text_color = ColorField(default="#000000")
    text_hover_color = ColorField(default="#000000")
    icon = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    panels = [
        FieldPanel("name"),
        MultiFieldPanel(
            [
                NativeColorPanel("bg_color"),
                NativeColorPanel("bg_hover_color"),
                NativeColorPanel("text_color"),
                NativeColorPanel("text_hover_color"),
            ],
            heading="Colors Info",
            classname="collapsible",
        ),
        ImageChooserPanel("icon"),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "experiences categories"


register_snippet(ExperiencesCategory)


class ExperiencePageTag(TaggedItemBase):
    content_object = ParentalKey(
        "ExperiencePage",
        related_name="tagged_items",
        on_delete=models.CASCADE,
    )


class ExperiencesPage(RoutablePageMixin, Page):
    max_count = 1
    parent_page_types = ["core.HomePage"]
    subpage_types = ["core.ExperiencePage"]

    def get_context(self, request, *args, **kwargs):
        """Adding custom stuff to our context."""
        context = super().get_context(request, *args, **kwargs)
        # Get all posts
        context["posts"] = pagination_wrapper(
            request,
            ExperiencePage.objects.live().public().order_by("-first_published_at"),
        )
        return context
    @route(r"^featured/$")
    def featured_experiences(self, request: HttpRequest):
        return TemplateResponse(
            request,
            self.get_template(request),
            {'posts': ExperiencePage.objects.live().filter(featured__exact=True).order_by("-first_published_at")}

        )


class ExperiencePage(RoutablePageMixin, Page):
    featured = models.BooleanField(
        default=False,
        help_text="Is this experience a featured experience",
        verbose_name="Set Featured"
    )
    description = models.TextField(
        default="",
        help_text="Description of Your experience",
        verbose_name="Description",
    )

    code = models.CharField(
        blank=True,
        max_length=6,
        default="",
        help_text="Six letter alpha-numeric code of you experience",
        verbose_name="Share Code",
    )
    exp_url = models.URLField(
        blank=True,
        default="",
        help_text="Url of your experience",
        verbose_name="Experience Url",
    )

    tags = ClusterTaggableManager(
        blank=True,
        help_text="Some tags",
        through=ExperiencePageTag,
        verbose_name="Tags",
    )
    vid_url = EmbedVideoField(
        blank=True,
        default="",
        help_text="Link to vid showcasing your experience",
        verbose_name="Video Url",
    )
    cover_img_url = models.URLField(
        blank=True,
        default="",
        help_text="Link for your cover Image",
        verbose_name="Cover Image Url",
    )

    no_players = models.PositiveIntegerField(
        blank=True,
        default=0,
        help_text="Max Number of Human Players in your experience",
        verbose_name="Number of Human Players",
    )
    no_bots = models.PositiveIntegerField(
        blank=True,
        default=0,
        help_text="Max Number of Bots in your experience",
        verbose_name="Number Of Bots",
    )
    categories = ParentalManyToManyField(
        "core.ExperiencesCategory", blank=False, help_text="Choose from the Category"
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("featured", classname="full",),
                FieldPanel("description", classname="full"),
                FieldPanel("categories", widget=forms.CheckboxSelectMultiple),
            ],
            heading="Basic Info",
            classname="collapsible",
        ),
        MultiFieldPanel(
            [
                FieldPanel("code", classname="full"),
                FieldPanel("exp_url", classname="full"),
            ],
            heading="Sharing Info",
            classname="collapsible",
        ),
        MultiFieldPanel(
            [
                FieldPanel("tags"),
                FieldPanel("cover_img_url", classname="full"),
                FieldPanel("vid_url", classname="full"),
            ],
            heading="Extra Info",
            classname="collapsible",
        ),
        MultiFieldPanel(
            [
                FieldPanel("no_players", classname="full"),
                FieldPanel("no_bots", classname="full"),
            ],
            heading="Settings info",
            classname="collapsible",
        ),
    ]

    parent_page_types = ["core.ExperiencesPage"]
    subpage_types = []

    @route(r"^edit/$")
    def edit_page(self, request: HttpRequest):
        if request.user.is_authenticated:
            if self.owner == request.user:
                from .views import edit_experience

                return edit_experience(request, self)
            else:
                logger.debug(
                    f"{request.user} tried to edit a experience they dont own exp: {request.path}"
                )
                return HttpResponse("Unauthorized", status=401)
        else:
            return redirect(LOGIN_URL)

    def is_experience_page(self):
        return True

def social_user(discord_id: int):
    """Returns a User object for a discord id"""
    try:
        usr = get_user_model().objects.get(
            id=SocialAccount.objects.get(uid=discord_id).user_id
        )
        return usr
    except ObjectDoesNotExist:
        return False


class ProfilePage(RoutablePageMixin, Page):
    max_count = 1
    parent_page_types = ["core.HomePage"]
    subpage_types = []

    def serve(self, request, view=None, args=None, kwargs=None):
        if request.user.is_authenticated:
            return super().serve(request, view, args, kwargs)
        else:
            return redirect(LOGIN_URL)

    def get_context(self, request, *args, **kwargs):
        l = kwargs.pop("list_experiences", None)
        user_acc = kwargs.pop("user", None)
        context = super().get_context(request, *args, **kwargs)
        all_posts = (
            ExperiencePage.objects.live()
            .public()
            .filter(owner=user_acc)
            .order_by("-first_published_at")
        )
        if not user_acc:
            user_acc = request.user
        if l:
            context["posts"] = pagination_wrapper(
                request,
                all_posts,
            )

            logger.debug(f"filtred {len(all_posts)} for {user_acc}")
        context["user"] = user_acc
        context["latest_post"] = all_posts.first()
        context["total_num_posts"] = len(all_posts)
        return context

    @route(r"^$")
    def root_profile_page(self, request):
        return redirect("/")

    @route(r"^(\d{18})/$", name="discord_id")
    def profile_page_view(self, request: HttpRequest, discord_id):
        user = social_user(discord_id)
        if user:
            logger.debug(f"fetch profile for {user}")
            return TemplateResponse(
                request,
                self.get_template(request),
                self.get_context(request, list_experiences=True, user=user),
            )
        else:
            return HttpResponse("Nope", status=404)

    @route(r"(\d{18})/experiences/$", name="discord_id")
    def user_experiences(self, request, discord_id):
        user = social_user(discord_id=discord_id)
        if user:
            logger.debug(f"fetch experiences for {user}")
            return TemplateResponse(
                request,
                "core/experiences_page.html",
                self.get_context(request=request, list_experiences=True, user=user),
            )
        else:
            return HttpResponse("User not Found", status=404)


class AvailableTags(models.Model):
    tags = models.TextField(
        blank=True, verbose_name="All available tags in BF 2042 Portal Rules editor"
    )
