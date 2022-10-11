from core.models import ExperiencePage, Profile
from django.core.management import BaseCommand
from loguru import logger


class Command(BaseCommand):
    """A command to get all tags from GameTools used for internal testing"""

    help = "A command to call various function that are required after migration"

    def add_arguments(self, parser):  # noqa: D102
        parser.add_argument(
            "--populate_liked_by",
            action="store_true",
            help="Gets all tags from game tools and saves to db",
        )

    def handle(self, *args, **options):  # noqa: D102
        if options.get("populate_liked_by", None):
            # a command to set liked_by in ExperiencePage according to Profile.liked
            logger.debug("populate_liked_by")
            for page in ExperiencePage.objects.all():
                page.liked_by.add(
                    *Profile.objects.all().filter(liked__title=page.title)
                )
            logger.debug("populate_liked_by finished")
