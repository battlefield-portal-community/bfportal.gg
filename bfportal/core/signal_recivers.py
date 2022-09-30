import os

import requests
from allauth.socialaccount.models import SocialAccount
from core.models import ExperiencePage
from django.contrib.sites.models import Site
from loguru import logger
from wagtail.signals import page_published


def send_to_discord(sender, **kwargs):
    """A signal receiver that accepts signal for ExperiencePage and posts to discord"""
    page: ExperiencePage
    page = kwargs["instance"]
    """Tries to send an embed to tell that new experience has been published

    discord channel specified by APPROVAL_SUCCESS_CHANNEL_WEBHOOK_ID env
    """
    if (
        isinstance(page, ExperiencePage)
        and page.first_publish
        and (token := os.getenv("APPROVAL_SUCCESS_CHANNEL_WEBHOOK_TOKEN", None))
        is not None
    ):
        logger.debug("Trying to send new published request")
        page.first_publish = False
        webhook_id = os.getenv("APPROVAL_SUCCESS_CHANNEL_WEBHOOK_ID")
        webhook_url = f"https://discord.com/api/webhooks/{webhook_id}/{token}"
        uid = -1
        admin_add = False
        try:
            uid = SocialAccount.objects.get(user_id=page.owner.id).uid
        except SocialAccount.DoesNotExist:
            admin_add = True

        domain = Site.objects.get_current().domain
        url = f"http://{domain}{page.get_url()}"
        data = {
            "content": "> **New Experience Posted :tada::tada:**",
            "embeds": [
                {
                    "url": url,
                    "title": page.title,
                    "description": page.description[0:200] + ".....",
                    "image": {
                        "url": page.cover_img_url
                        if page.cover_img_url
                        else "https://super-static-assets.s3.amazonaws.com/19d9fbc6-6292-4be8-ac70-5a186b556054%2Fimages%2Fb6495922-b4c7-4002-9c3d-56bfaa5b98b5.jpg"  # noqa: E501
                    },
                    "fields": [
                        {
                            "name": "Author",
                            "value": f"<@{uid}>" if not admin_add else "**admin**",
                            "inline": True,
                        },
                        {
                            "name": "Submitted on",
                            "value": f"<t:{int(page.first_published_at.timestamp())}>",
                            "inline": True,
                        },
                        {
                            "name": "Category",
                            "value": ":white_small_square: " + f"\u200B{page.category}",
                        },
                        {
                            "name": "Sub Categories",
                            "value": ":white_small_square: "
                            + "".join([f"`{i}` " for i in page.sub_categories.all()]),
                        },
                        {
                            "name": "Tags",
                            "value": ":white_small_square: "
                            + "".join([f"`{i}` " for i in page.tags.all()]),
                        },
                    ],
                }
            ],
            "token": token,
            "components": [
                {
                    "type": 1,
                    "components": [
                        {
                            "type": 2,
                            "style": 5,
                            "url": url,
                            "label": "link",
                        }
                    ],
                }
            ],
        }
        if page.featured:
            data["embeds"][0]["fields"].insert(
                2,
                {
                    "name": "Featured",
                    "value": ":white_check_mark:",
                    "inline": True,
                },
            )
        headers = {"Content-Type": "application/json"}
        result = requests.post(webhook_url, json=data, headers=headers)
        try:
            result.raise_for_status()
            logger.debug(f"Experience embed for {page.title} sent successfully ")
            page.save()
        except requests.exceptions.HTTPError as err:
            logger.debug(f"Error {err} while sending new experience for {page.title}")
            print(result.content)


logger.debug("registering signal receivers")
page_published.connect(send_to_discord)
