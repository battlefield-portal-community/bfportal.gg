import json

import requests
from core.models import AvailableTags
from django.core.management import BaseCommand


class Command(BaseCommand):
    """A command to get all tags from GameTools used for internal testing"""

    help = "Gets all the tags from gametools"

    def add_arguments(self, parser):  # noqa: D102
        parser.add_argument(
            "--get_tags",
            action="store_true",
            help="Gets all tags from game tools",
        )

    def handle(self, *args, **options):  # noqa: D102
        if options.get("get_tags", None):
            all_tags_json = requests.get(
                "https://api.gametools.network/bf2042/availabletags/?lang=en-us"
            ).json()["availableTags"]
            tags = [
                tag_dict["metadata"]["translations"][0]["localizedText"]
                for tag_dict in all_tags_json
            ]
            AvailableTags.objects.all().delete()
            new_obj = AvailableTags(tags=json.dumps(tags))
            new_obj.save()
