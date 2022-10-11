from core.helper import validate_image_link
from django.db import models
from markdownx.models import MarkdownxField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.snippets.models import register_snippet
from wagtailsvg.edit_handlers import SvgChooserPanel
from wagtailsvg.models import Svg


class BaseCategory(models.Model):
    """Class defining properties of BaseCategory"""

    name = models.CharField(max_length=255)
    icon = models.ForeignKey(
        Svg,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    visible = models.BooleanField(
        help_text="Show Category on home page?", default=True, null=False
    )
    selectable_on_form = models.BooleanField(
        help_text="Should this Category be selectable in submit form",
        default=True,
        null=False,
    )
    not_ready = models.BooleanField(
        default=False,
        help_text="If set, Shows Coming soon page for this category",
        null=False,
    )
    description = MarkdownxField(
        blank=True,
        null=False,
        help_text="description of this category that is shown on /category/",
    )

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

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("name"),
                FieldPanel("description"),
                SvgChooserPanel("icon"),
                FieldPanel("visible"),
                FieldPanel("selectable_on_form"),
                FieldPanel("not_ready"),
            ],
            classname="collapsed",
            heading="Category info",
        ),
        MultiFieldPanel(
            [
                FieldPanel("meta_title"),
                FieldPanel("meta_description"),
                FieldPanel("meta_image"),
            ],
            classname="collapsed",
            heading="Preview Embed Override",
        ),
    ]

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class ExperiencesCategory(BaseCategory):
    """Class defining properties of experience category tag"""

    class Meta:
        verbose_name_plural = "Main Categories"


class SubCategory(BaseCategory):
    """Class defining properties of experience sub categories"""

    class Meta:
        verbose_name_plural = "Sub Categories"


register_snippet(ExperiencesCategory)
register_snippet(SubCategory)
