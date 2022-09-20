from core.helper import get_tags_from_gt_api
from django.core.management import BaseCommand


class Command(BaseCommand):
    """Command that is used to develop other command and test stuff"""

    def handle(self, *args, **options):  # noqa: D102
        print(get_tags_from_gt_api())
