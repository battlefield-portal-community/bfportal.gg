import pydantic
from bf6.models.bf_experience_export import ExperienceExport
from bf6.models.categories import ScriptsCategory
from core.helper import user_to_api_response
from core.models.pages import CustomBasePage
from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from embed_video.fields import EmbedVideoField
from loguru import logger
from markdownx.models import MarkdownxField
from modelcluster.fields import ParentalManyToManyField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.models import Page
from wagtail.search import index
from wagtailautocomplete.edit_handlers import AutocompletePanel

from bfportal.settings.base import LOGIN_URL


class SnippetPage(RoutablePageMixin, CustomBasePage):
    """Class defining properties of a script page."""

    featured = models.BooleanField(
        default=False,
        help_text="make this rules page featured",
        verbose_name="Set Featured",
    )
    trending = models.BooleanField(
        default=False,
        null=False,
        help_text="Is this rules trending?",
        verbose_name="Set Trending",
    )
    description = MarkdownxField(
        default="",
        help_text="Description of your script/rule blocks",
        verbose_name="Description",
    )

    vid_url = EmbedVideoField(
        blank=True,
        default="",
        help_text="Link to vid showcasing/explaing your Snippet",
        verbose_name="Video Url",
    )

    category = models.ForeignKey(
        ScriptsCategory,
        blank=False,
        null=True,
        on_delete=models.SET_NULL,
        help_text="Choose Script Type",
        related_name="+",
    )
    code = models.TextField(blank=False, null=True, default="")
    exp_json = models.JSONField(blank=True, null=True, default=dict)

    first_publish = models.BooleanField(default=True, null=False)
    liked_by = models.ManyToManyField("core.Profile", blank=True)
    creators = ParentalManyToManyField(
        "auth.User", blank=True, help_text="choose creators"
    )
    allow_editing = models.BooleanField(default=False, null=False)
    is_mock = models.BooleanField(
        default=False, null=False, help_text="Is this a mock script?"
    )
    parent_page_types = ["bf6.ScriptsListingPage"]
    subpage_types = []

    search_fields = Page.search_fields + [
        index.SearchField("title"),
        index.SearchField("description"),
        index.SearchField("code"),
    ]
    content_panels = (
        Page.content_panels
        + [
            MultiFieldPanel(
                [
                    FieldPanel("featured", classname="full", permission="superuser"),
                    FieldPanel("trending", classname="full", permission="superuser"),
                ],
                heading="Admin only",
            ),
            MultiFieldPanel(
                [
                    FieldPanel("allow_editing"),
                    AutocompletePanel("owner", target_model="core.Profile"),
                    FieldPanel("description", classname="full"),
                    FieldPanel("category", widget=forms.RadioSelect),
                    AutocompletePanel("creators", target_model="core.Profile"),
                ],
                heading="Description, Categories, Creators",
                classname="collapsed",
            ),
            MultiFieldPanel(
                [
                    FieldPanel("vid_url", classname="full"),
                ],
                heading="Video Showcasing the snippet",
                classname="collapsed",
            ),
            MultiFieldPanel(
                [
                    FieldPanel("code", classname="full"),
                    FieldPanel("exp_json", classname="full"),
                ],
                heading="Code, Json",
                classname="collapsed",
            ),
        ]
        + [CustomBasePage.content_panels[-1]]
    )

    def clean(self):
        """Custom clean method to validate the experience json."""
        try:
            ExperienceExport(**self.exp_json)
        except pydantic.ValidationError as e:
            exp_errors = []

            for error in e.errors():
                location = ".".join(str(loc) for loc in error["loc"])
                exp_errors.append(f"{location}: {error['msg']}")
            raise ValidationError({"exp_json": ["\n".join(exp_errors)]})

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
        return self.render(request=request, template="coming_soon.html")

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
