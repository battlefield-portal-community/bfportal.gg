import requests
from loguru import logger
from taggit.models import Tag


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
