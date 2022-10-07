from functools import partial

import bleach
import markdown
import requests
from bleach.css_sanitizer import ALLOWED_CSS_PROPERTIES  # noqa: F401
from django.conf import settings
from django.utils.safestring import mark_safe
from loguru import logger
from taggit.models import Tag

GT_BASE_URL = "https://api.gametools.network/bf2042/playground/?{}&blockydata=false&lang=en-us&return_ownername=false"


def markdownify(text):
    """Called by MarkdownX to get markdown -> html"""
    # Bleach settings
    whitelist_tags = getattr(
        settings, "MARKDOWNIFY_WHITELIST_TAGS", bleach.sanitizer.ALLOWED_TAGS
    )
    whitelist_attrs = getattr(
        settings, "MARKDOWNIFY_WHITELIST_ATTRS", bleach.sanitizer.ALLOWED_ATTRIBUTES
    )
    whitelist_styles = getattr(
        settings,
        "MARKDOWNIFY_WHITELIST_STYLES",
        bleach.css_sanitizer.ALLOWED_CSS_PROPERTIES,
    )
    whitelist_protocols = getattr(
        settings, "MARKDOWNIFY_WHITELIST_PROTOCOLS", bleach.sanitizer.ALLOWED_PROTOCOLS
    )

    # Markdown settings
    strip = getattr(settings, "MARKDOWNIFY_STRIP", True)
    extensions = getattr(settings, "MARKDOWNIFY_MARKDOWN_EXTENSIONS", [])

    # Bleach Linkify
    linkify = None
    linkify_text = getattr(settings, "MARKDOWNIFY_LINKIFY_TEXT", True)

    if linkify_text:
        linkify_parse_email = getattr(
            settings, "MARKDOWNIFY_LINKIFY_PARSE_EMAIL", False
        )
        linkify_callbacks = getattr(settings, "MARKDOWNIFY_LINKIFY_CALLBACKS", None)
        linkify_skip_tags = getattr(settings, "MARKDOWNIFY_LINKIFY_SKIP_TAGS", None)
        linkifyfilter = bleach.linkifier.LinkifyFilter

        linkify = [
            partial(
                linkifyfilter,
                callbacks=linkify_callbacks,
                skip_tags=linkify_skip_tags,
                parse_email=linkify_parse_email,
            )
        ]

    # Convert markdown to html
    html = markdown.markdown(text, extensions=extensions)

    # Sanitize html if wanted
    if getattr(settings, "MARKDOWNIFY_BLEACH", True):
        css_sanitizer = bleach.css_sanitizer.CSSSanitizer(
            allowed_css_properties=whitelist_styles
        )

        cleaner = bleach.Cleaner(
            tags=whitelist_tags,
            attributes=whitelist_attrs,
            css_sanitizer=css_sanitizer,
            protocols=whitelist_protocols,
            strip=strip,
            filters=linkify,
        )

        html = cleaner.clean(html)

    return mark_safe(html)


def get_tags_from_gt_api() -> list:
    """Gets tags from GameTools api."""
    all_tags_json = requests.get(
        "https://api.gametools.network/bf2042/availabletags/?lang=en-us"
    ).json()["availableTags"]
    return [
        tag_dict["metadata"]["translations"][0]["localizedText"]
        for tag_dict in all_tags_json
    ]


def save_tags_from_gt_api():
    """Saves non existing tags in db"""
    tags_added = []
    for tag in get_tags_from_gt_api():
        if not Tag.objects.filter(name__exact=tag).exists():
            Tag(name=tag).save()
            tags_added.append(tag)
        else:
            logger.debug(f"{tag} exists in db")
    logger.debug(f"Added Tags :- {tags_added}")
