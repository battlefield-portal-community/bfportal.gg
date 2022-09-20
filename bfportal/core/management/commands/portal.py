from core.helper import save_tags_from_gt_api
from django.core.management import BaseCommand


class Command(BaseCommand):
    """A command to get all tags from GameTools used for internal testing"""

    help = "Gets all the tags from gametools"

    def add_arguments(self, parser):  # noqa: D102
        parser.add_argument(
            "--get_tags",
            action="store_true",
            help="Gets all tags from game tools and saves to db",
        )

    def handle(self, *args, **options):  # noqa: D102
        if options.get("get_tags", None):
            save_tags_from_gt_api()
