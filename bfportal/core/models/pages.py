from typing import TYPE_CHECKING

from core.helper import validate_image_link
from core.models.categories import ExperiencesCategory, SubCategory
from core.models.helper import pagination_wrapper
from django.apps import apps
from django.db import models
from django.template.response import TemplateResponse
from loguru import logger
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, path, route
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page

if TYPE_CHECKING:
    from .experience import ExperiencePage as ExperiencePageModel


class ExtraContent(blocks.StreamBlock):
    """Class defining extra fields available to all pages"""

    heading = blocks.CharBlock(form_classname="full title")
    cover_image = ImageChooserBlock()
    text = blocks.RichTextBlock()
    raw_html = blocks.RawHTMLBlock()

    class Meta:
        template = "core/blocks/extra_content.html"
        icon = "user"
        required = False
        help_text = "Custom Content for a page"


class CustomBasePage(Page):
    """Base class for all pages in the app

    Require to expose ExtraContent to all child pages
    """

    extra_content = StreamField(ExtraContent(), blank=True, use_json_field=True)
    meta_title = models.CharField(
        blank=True,
        null=True,
        help_text="If set this title is displayed in embeds",
        max_length=255,
    )
    meta_description = models.TextField(
        blank=True,
        null=True,
        help_text="If set this description is displayed in embeds",
    )
    meta_image = models.URLField(
        blank=True,
        null=True,
        help_text="If set this image is displayed in embeds. Recommend size 1200x630px",
        validators=[validate_image_link],
    )

    content_panels = Page.content_panels + [
        FieldPanel(
            "extra_content",
            classname="collapsed",
        )
    ]
    promote_panels = [
        MultiFieldPanel(
            [
                FieldPanel("meta_title"),
                FieldPanel("meta_description"),
                FieldPanel("meta_image"),
            ],
            classname="collapsible",
            heading="Preview Embed Override",
        )
    ] + Page.promote_panels

    class Meta:
        abstract = True


class BlogPage(CustomBasePage):
    """Class for future usage"""

    pass


class HomePage(RoutablePageMixin, CustomBasePage):
    """Class defining the 'index' page of the website"""

    max_count = 1
    parent_page_types = ["wagtailcore.Page"]
    subpage_types = ["core.ExperiencesPage", "core.ProfilePage", "core.BlogPage"]

    @route(r"^$")
    def base(self, request):  # noqa: D102
        logger.debug("base")
        return TemplateResponse(
            request,
            self.get_template(request),
            self.get_context(request, filter_trending=True),
        )

    @route(r"^submit/$")
    def submit_exp(self, request):  # noqa: D102
        from core.views import submit_experience

        return submit_experience(request, self)

    def get_context(self, request, *args, **kwargs):  # noqa: D102
        ExperiencePage: ExperiencePageModel = apps.get_model("core", "ExperiencePage")

        filter_trending = kwargs.pop("filter_trending", False)
        context = super().get_context(request, *args, **kwargs)
        posts = pagination_wrapper(
            request,
            ExperiencePage.objects.live().public().order_by("-first_published_at"),
        )

        context["categories"] = list(ExperiencesCategory.objects.all()) + list(
            SubCategory.objects.all()
        )
        context["posts"] = posts
        if filter_trending:
            context["trending_posts"] = (
                ExperiencePage.objects.filter(trending=True)
                .live()
                .public()
                .order_by("-first_published_at")
            )
        return context

    @path("tutorials/")
    def serve_coming_soon(self, request):
        """Returns coming soon page as these are not yet ready."""
        return self.render(request=request, template="coming_soon.html")

    @path("category/<slug:cat>/")
    def serve_category_page(self, request, cat: str):
        """Returns template with post of a category if cat present in db"""
        ExperiencePage: ExperiencePageModel = apps.get_model("core", "ExperiencePage")
        main_cat, sub_cat = None, None
        main_cat: ExperiencesCategory | None
        sub_cat: SubCategory | None

        cat = cat.replace("_", " ")
        cat_object: ExperiencesCategory | SubCategory | None
        if cat_object := ExperiencesCategory.objects.filter(name__iexact=cat).first():
            main_cat = cat_object
        elif cat_object := SubCategory.objects.filter(name__iexact=cat).first():
            sub_cat = cat_object
        else:
            return self.render(request=request, template="404.html")

        if cat_object.not_ready:
            return self.render(request=request, template="coming_soon.html")

        request.GET = request.GET.copy()
        if main_cat:
            request.GET["category"] = main_cat.name
        if sub_cat:
            request.GET["sub_cat"] = sub_cat.name
        context = super().get_context(request)
        posts = pagination_wrapper(
            request,
            ExperiencePage.objects.live().public().order_by("-first_published_at"),
        )
        context["cat_description"] = cat_object.description
        if (
            cat_object.meta_title
            or cat_object.meta_description
            or cat_object.meta_image
        ):
            if not cat_object.meta_title:
                cat_object.name = cat_object.meta_title
                cat_object.save()
            context["page"] = cat_object
        context["posts"] = posts
        context["no_extra_content"] = True
        return TemplateResponse(request, self.get_template(request), context)


class DiscordScheduledEvent(models.Model):
    """Model representing a discord event"""

    title = models.CharField(
        blank=False,
        null=True,
        help_text="Name of the event (only for admin panel)",
        max_length=255,
    )
    server_id = models.CharField(
        default="870246147455877181",
        blank=False,
        null=True,
        max_length=50,
        help_text="ID of the server in which event is taking place [default: bfportal.gg discord server's id]",
    )
    event_id = models.CharField(
        blank=False,
        null=True,
        max_length=50,
        help_text="ID of the event to show on website",
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("title", classname="full"),
                FieldPanel("event_id", classname="full"),
                FieldPanel("server_id", classname="full"),
            ],
            classname="collapsable",
        )
    ]
