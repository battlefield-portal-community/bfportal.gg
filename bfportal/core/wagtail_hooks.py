import os

import requests
from allauth.socialaccount.models import SocialAccount
from core.models import ExperiencePage
from django.http import HttpRequest
from loguru import logger
from wagtail import hooks

logger.debug("Registering hooks")


@hooks.register("after_publish_page")
def send_new_publish_embed(request: HttpRequest, page: ExperiencePage):
    """Tries to send an embed to tell that new experience has been published

    discord channel specified by APPROVAL_SUCCESS_CHANNEL_WEBHOOK_ID env
    """
    logger.debug("send_new_publish_embed called")

    if (
        isinstance(page, ExperiencePage)
        and page.first_publish
        and (token := os.getenv("APPROVAL_SUCCESS_CHANNEL_WEBHOOK_TOKEN", None))
        is not None
    ):
        page.first_publish = False
        webhook_id = os.getenv("APPROVAL_SUCCESS_CHANNEL_WEBHOOK_ID")
        webhook_url = f"https://discord.com/api/webhooks/{webhook_id}/{token}"
        uid = SocialAccount.objects.get(user_id=page.owner.id).uid
        url = f"{request.scheme}://{request.get_host()}{page.get_url()}"
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
                        {"name": "Author", "value": f"<@{uid}>", "inline": True},
                        {
                            "name": "Submitted on",
                            "value": f"<t:{int(page.first_published_at.timestamp())}>",
                            "inline": True,
                        },
                        {
                            "name": "Category",
                            "value": ":white_small_square: "
                            + "\u200B".join([str(i) for i in page.categories.all()]),
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
        except requests.exceptions.HTTPError as err:
            logger.debug(f"Error {err} while sending new experience for {page.title}")
            print(result.content)
        else:
            logger.debug("Experience embed for {page.title} sent successfully ")
