from typing import Optional, TypedDict

from core.models.categories import ExperiencesCategory
from core.models.helper import pagination_wrapper
from core.models.pages import CustomBasePage
from django import forms
from django.contrib.auth.models import User
from django.db import models
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from embed_video.fields import EmbedVideoField
from loguru import logger
from markdownx.models import MarkdownxField
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from taggit.models import TaggedItemBase
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.models import Page
from wagtailautocomplete.edit_handlers import AutocompletePanel

from bfportal.settings.base import LOGIN_URL


class UserApiResponse(TypedDict):
    """Type definition for user api response"""

    id: Optional[str]
    username: str
    discriminator: Optional[str]


def user_to_api_response(user: User) -> UserApiResponse:
    """Converts a user to a dict to be used in api response"""
    if social_account := user.socialaccount_set.first():
        social_account = social_account.extra_data
        return {
            "id": social_account["id"],
            "username": social_account["username"],
            "discriminator": social_account["discriminator"],
        }
    return {"username": user.username}


class ExperiencePageTag(TaggedItemBase):
    """Class to link a tag to an Experience page"""

    content_object = ParentalKey(
        "ExperiencePage",
        related_name="tagged_items",
        on_delete=models.CASCADE,
    )


class ExperiencePage(RoutablePageMixin, CustomBasePage):
    """Class defining properties of an experience page

    This is equivalent to a post in a blog
    """

    featured = models.BooleanField(
        default=False,
        help_text="Is this experience a featured experience",
        verbose_name="Set Featured",
    )
    trending = models.BooleanField(
        default=False,
        null=False,
        help_text="Is this experience trending?",
        verbose_name="Set Trending",
    )
    description = MarkdownxField(
        default="",
        help_text="Description of Your experience",
        verbose_name="Description",
    )

    code = models.CharField(
        blank=True,
        max_length=6,
        default="",
        help_text="Six letter alpha-numeric code of you experience",
        verbose_name="Experience Code",
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
        max_length=1000,
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
    category = models.ForeignKey(
        ExperiencesCategory,
        blank=False,
        null=True,
        on_delete=models.SET_NULL,
        help_text="Choose Main Category",
        related_name="+",
    )
    sub_categories = ParentalManyToManyField(
        "core.SubCategory", blank=True, help_text="Choose Sub Category Category"
    )

    bugged = models.BooleanField(
        default=False,
        null=False,
        help_text="Is the experience bugged",
        verbose_name="Bugged ?",
    )
    bugged_report = ParentalManyToManyField(
        "auth.User",
        blank=True,
        help_text="People who have reported this exp is bugged",
        related_name="bugged_report",
    )

    broken = models.BooleanField(
        default=False,
        null=False,
        help_text="Is the experience broken",
        verbose_name="Broken ?",
    )
    broken_report = ParentalManyToManyField(
        "auth.User",
        blank=True,
        help_text="People who have reported this is exp broken",
        related_name="broken_report",
    )

    xp_farm = models.BooleanField(
        default=False,
        null=False,
        help_text="Is the experience an xp farm",
        verbose_name="XP farm ?",
    )
    xp_farm_report = ParentalManyToManyField(
        "auth.User",
        blank=True,
        help_text="People who have reported this is exp an xp farm",
        related_name="xp_farm_report",
    )

    first_publish = models.BooleanField(default=True, null=False)

    liked_by = models.ManyToManyField("core.Profile", blank=True)

    creators = ParentalManyToManyField(
        "auth.User", blank=True, help_text="choose creators"
    )

    allow_editing = models.BooleanField(default=False, null=False)
    is_mock = models.BooleanField(
        default=False, null=False, help_text="Is this a mock experience ?"
    )

    parent_page_types = ["core.ExperiencesPage"]
    subpage_types = []

    content_panels = (
        Page.content_panels
        + [
            MultiFieldPanel(
                [
                    FieldPanel("featured", classname="full", permission="superuser"),
                    FieldPanel("trending", classname="full", permission="superuser"),
                    *[
                        FieldPanel(field, classname="full", permission="superuser")
                        for field in ["bugged", "broken", "xp_farm"]
                    ],
                ],
                heading="Admin only",
            ),
            MultiFieldPanel(
                [
                    FieldPanel("allow_editing"),
                    AutocompletePanel("owner", target_model="core.Profile"),
                    FieldPanel("description", classname="full"),
                    FieldPanel("category", widget=forms.RadioSelect),
                    FieldPanel("sub_categories", widget=forms.CheckboxSelectMultiple),
                    AutocompletePanel("creators", target_model="core.Profile"),
                ],
                heading="Title, Description, Categories, Creators",
                classname="collapsed",
            ),
            MultiFieldPanel(
                [
                    FieldPanel("code", classname="full"),
                    FieldPanel("exp_url", classname="full"),
                ],
                heading="Experience Url and Code",
                classname="collapsed",
            ),
            MultiFieldPanel(
                [
                    FieldPanel("tags"),
                    FieldPanel("cover_img_url", classname="full"),
                    FieldPanel("vid_url", classname="full"),
                ],
                heading="Tags, cover img, vid",
                classname="collapsed",
            ),
            MultiFieldPanel(
                [
                    FieldPanel("no_players", classname="full"),
                    FieldPanel("no_bots", classname="full"),
                ],
                heading="Players, Bots",
                classname="collapsed",
            ),
            *[
                MultiFieldPanel(
                    [
                        AutocompletePanel(
                            f"{field}_report",
                            target_model="core.Profile",
                            classname="full",
                        ),
                    ],
                    heading=f"{field.replace('_', ' ').capitalize()} info",
                    classname="collapsed",
                )
                for field in ["bugged", "broken", "xp_farm"]
            ],
        ]
        + [CustomBasePage.content_panels[-1]]
    )

    @property
    def like_count(self):
        """Return the number of likes this experience has."""
        return self.liked_by.count()

    @property
    def exp_creators(self):
        """Return the creators of this experience."""
        creators = [user_to_api_response(self.owner)]
        creators.extend(
            [user_to_api_response(creator) for creator in self.creators.all()]
        )
        return creators

    @route(r"^edit/$")
    def edit_page(self, request: HttpRequest):  # noqa: D102
        if request.user.is_authenticated:
            if self.owner == request.user:
                from core.views import edit_experience

                return edit_experience(request, self)
            else:
                logger.debug(
                    f"{request.user} tried to edit a experience they dont own exp: {request.path}"
                )
                return HttpResponse("Unauthorized", status=401)
        else:
            return redirect(LOGIN_URL)

    @route(r"^delete/$")
    def delete_experience(self, request: HttpRequest):  # noqa: D102
        if request.user.is_authenticated:
            if self.owner == request.user:
                # todo actually delete it
                print("Delete experience")
                return redirect(request.META["HTTP_REFERER"])
            else:
                logger.debug(
                    f"{request.user} tried to delete a experience they dont own exp: {request.path}"
                )
                return HttpResponse("Unauthorized", status=401)
        else:
            return redirect(LOGIN_URL)

    @staticmethod
    def is_experience_page():  # noqa: D102
        return True


class ExperiencesPage(RoutablePageMixin, CustomBasePage):
    """Class defining page that lists all experiences"""

    max_count = 1
    parent_page_types = ["core.HomePage"]
    subpage_types = ["core.ExperiencePage", "core.BlogPage"]

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
    def featured_experiences(self, request: HttpRequest):  # noqa: D102
        return TemplateResponse(
            request,
            self.get_template(request),
            {
                "posts": ExperiencePage.objects.live()
                .filter(featured__exact=True)
                .order_by("-first_published_at"),
            },
        )
