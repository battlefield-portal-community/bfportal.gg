import operator
from datetime import datetime, timezone
from functools import reduce
from typing import TYPE_CHECKING

from core.utils.helper import safe_cast
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.db.models import Q
from django.db.models import Value as V
from django.db.models.functions import Concat
from django.http import HttpRequest
from loguru import logger

if TYPE_CHECKING:
    from .categories import SubCategory
    from .experience import ExperiencePage


def apply_filters(request: HttpRequest, posts: models.query.QuerySet):
    """Applies get param filters to database and returns posts"""
    all_posts = posts
    if experience := request.GET.get("experience", None):
        logger.debug(f"Experience Name :- {experience}")
        all_posts = all_posts.filter(title__icontains=experience)

    from_date = request.GET.get("From", None)
    if from_date is None or from_date == "":
        from_date = datetime.utcfromtimestamp(0)  # use date provided else use epoch
    else:
        from_date = datetime.fromisoformat(from_date)

    to_date = request.GET.get("To")
    if to_date is None or to_date == "":
        to_date = datetime.utcnow()  # use date provided else use current time
    else:
        to_date = datetime.fromisoformat(to_date)

    from_date = from_date.replace(tzinfo=timezone.utc)
    to_date = to_date.replace(tzinfo=timezone.utc)

    logger.debug(f"From {from_date} to {to_date}")
    all_posts = all_posts.filter(first_published_at__range=(from_date, to_date))
    if username := request.GET.get("creator", ""):
        if username != "":
            all_posts = all_posts.annotate(
                discord_username=Concat(
                    "owner__username",
                    V(" "),
                    "owner__first_name",
                    V(" "),
                    "owner__last_name",
                )
            )
            logger.debug(f"username is {username}")
            all_posts = all_posts.filter(discord_username__icontains=username)

    if tags := request.GET.getlist("tag", None):
        logger.debug(tags)
        all_posts = all_posts.filter(tags__name__in=tags).distinct()

    if category := request.GET.getlist("category", None):
        category = list(map(str.lower, category))
        post: ExperiencePage
        all_posts = all_posts.filter(
            reduce(operator.or_, (Q(category__name__iexact=cat) for cat in category))
        )
    if sub_cats := request.GET.getlist("sub_cat", None):
        sub_cats: [SubCategory, ...]
        sub_cats = list(map(str.lower, sub_cats))
        post: ExperiencePage
        all_posts = all_posts.filter(
            reduce(
                operator.or_, (Q(sub_categories__name__iexact=cat) for cat in sub_cats)
            )
        )
    if tags or category or sub_cats:
        logger.debug(
            f"filtered {len(all_posts)} experiences for tags {tags}, cat [{category}, sub cat {sub_cats}]"
        )
    if sort := request.GET.get("sort", None):
        match sort:
            case "like":
                all_posts = all_posts.order_by("-likes")
            case "latest":
                pass

    return all_posts


def pagination_wrapper(request: HttpRequest, posts: models.query.QuerySet) -> Paginator:
    """Returns paginated result for a query"""
    paginator = Paginator(apply_filters(request, posts), request.GET.get("n", 12))
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
