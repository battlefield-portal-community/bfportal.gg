import operator
import re
from functools import reduce

import requests
from core.models import ExperiencePage
from django.core.management import BaseCommand
from django.db.models import Q
from loguru import logger


class Command(BaseCommand):
    """A command to fix cover_img_url for ExperiencePage"""

    help = "Tries to fix cover_img_url in the db"

    def handle(self, *args, **options):  # noqa: D102
        pages = ExperiencePage.objects.exclude(
            reduce(
                operator.or_,
                (Q(cover_img_url__iendswith=x) for x in ["png", "jpeg", "jpg"]),
            )
        )
        logger.debug(f"{len(pages)} pages might be broken....")
        for index, page in enumerate(pages):
            fixed = False
            if len(page.cover_img_url):
                if "www.google.com" not in page.cover_img_url:
                    try:
                        header_resp = requests.head(
                            page.cover_img_url, allow_redirects=True
                        )
                        if not header_resp.headers.get("content-type", "").startswith(
                            "image"
                        ):
                            fixed = True
                            if page.cover_img_url.startswith("https://imgur.com/a"):
                                resp = requests.post(
                                    "https://imgur-direct-links.herokuapp.com/",
                                    data={
                                        "imgur_url_field": f"{page.cover_img_url}",
                                        "button_get_links": "get_links",
                                        "list_textarea": "",
                                    },
                                )
                                if links := re.search(
                                    r'<textarea id="list_textarea" name="list_textarea" readonly rows="10">(.*?)\s</textarea>',  # noqa: E501
                                    resp.text,
                                ):
                                    page.cover_img_url = links.groups()[0]
                            else:
                                resp = requests.get(
                                    page.cover_img_url, allow_redirects=True
                                )
                                if search_result := re.search(
                                    r'<meta property="og:image"\Wcontent="(.*?)">',
                                    resp.text,
                                ):
                                    url = search_result.groups()[0]
                                    if "drive.google.com" in page.cover_img_url:
                                        url = url.split("=")[0]
                                    page.cover_img_url = url
                    except requests.exceptions.ConnectionError:
                        logger.debug(
                            f"host for image {page.cover_img_url} is down.... reset img to none"
                        )
                        page.cover_img_url = ""
                else:
                    fixed = True
                    page.cover_img_url = ""

            if fixed:
                page.save()
                logger.debug(f"fixed {page} {index+1} / {len(pages)}")
