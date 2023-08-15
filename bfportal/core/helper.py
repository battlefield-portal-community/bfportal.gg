import os
from functools import partial
from typing import TYPE_CHECKING, NotRequired, TypedDict, Union

import bleach
import markdown
import requests
from bleach.css_sanitizer import ALLOWED_CSS_PROPERTIES  # noqa: F401
from cachetools import TTLCache, cached
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe
from loguru import logger
from taggit.models import Tag

if TYPE_CHECKING:
    from django.contrib.auth.models import User as UserType

GT_BASE_URL = "https://api.gametools.network/bf2042/playground/?{}&blockydata=false&lang=en-us&return_ownername=false"
User: "UserType"
User = get_user_model()


class UserApiResponse(TypedDict):
    """Type definition for user api response"""

    id: NotRequired[Union[str | None]]
    username: str


def get_scheduled_events(event_id: str, server_id: str = "870246147455877181") -> dict:
    """Tries to retrieve Scheduled events via discord API"""
    if len(DISCORD_TOKEN := os.getenv("DISCORD_BOT_TOKEN", "")):
        headers = {
            "Authorization": f"Bot {DISCORD_TOKEN}",
            "content-type": "application/json",
        }
        resp = requests.get(
            f"https://discord.com/api/v10/guilds/{server_id}/scheduled-events",
            headers=headers,
        )
        return resp.json()
    else:
        logger.warning(
            "Unable to get scheduled events... DISCORD_BOT_TOKEN not provided"
        )


def validate_image_link(link: str):
    """Checks if the url is a direct url to an image"""
    try:
        header_resp = requests.head(link, allow_redirects=True)
        if not header_resp.headers["content-type"].startswith("image"):
            raise forms.ValidationError(
                "Image url is invalid, make sure it is a direct link to the image"
            )
        return link
    except requests.ConnectionError:
        raise forms.ValidationError("Unable to access image")


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

    if tags_added:
        logger.debug(f"Added Tags :- {tags_added}")

    if len(cloudflare_auth_key := os.getenv("CLOUDFLARE_AUTH_KEY", "")):
        if len(cloudflare_auth_email := os.getenv("CLOUDFLARE_AUTH_EMAIL", "")):
            if len(cloudflare_zone_id := os.getenv("CLOUDFLARE_ZONE_ID", "")):
                requests.post(
                    f"https://api.cloudflare.com/client/v4/zones/{cloudflare_zone_id}/purge_cache",
                    json={
                        "files": [
                            "https://bfportal.gg/api/categories/?q="
                            "https://bfportal.gg/api/tags/?q="
                        ]
                    },
                    headers={
                        "X-Auth-Email": cloudflare_auth_email,
                        "X-Auth-Key": cloudflare_auth_key,
                        "Content-Type": "application/json",
                    },
                )


@cached(cache=TTLCache(maxsize=1024, ttl=60 * 60))  # cache for 1 hour
def user_to_api_response(user: User) -> UserApiResponse:
    """Converts a user to a dict to be used in api response"""
    if social_account := user.socialaccount_set.first():
        social_account = social_account.extra_data
        return {
            "id": social_account["id"],
            "username": social_account["username"],
        }
    return {"username": user.username, "id": None}
