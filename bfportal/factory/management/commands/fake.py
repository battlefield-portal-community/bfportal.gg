import datetime
import string
from random import choice, choices, randint
from uuid import uuid4

from core.models import ExperiencePage, ExperiencesCategory, ExperiencesPage
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.utils.text import slugify
from faker import Faker
from loguru import logger


class Command(BaseCommand):
    """A command that generates fake data to populate experiences in Database"""

    help = "Generates fake data"

    def add_arguments(self, parser):  # noqa: D102
        parser.add_argument("no_of_pages", metavar="N", type=int, nargs="+")
        # Named (optional) arguments
        parser.add_argument(
            "--generate",
            action="store_true",
            help="Generates Fake Data",
        )

    def handle(self, *args, **options):
        """Handler for command, handles the generation of data"""
        if options["generate"]:
            factory = Faker()
            cats = ExperiencesCategory.objects.all()
            owner = [
                user for user in get_user_model().objects.all() if not user.is_superuser
            ]
            tags = [factory.word() for i in range(20)]
            experiences_page = ExperiencesPage.objects.first()
            page_count = options.get("no_of_pages", [0])[0]
            logger.critical("delete all Experience Pages [y/n] ")
            exp_pages = ExperiencePage.objects.all()
            if input().lower() == "y":
                if len(exp_pages):
                    for _ in exp_pages:
                        _.delete()

            for i in range(page_count):
                t = f"{factory.word()} {factory.word()}"
                page = ExperiencePage(
                    title=t,
                    slug=slugify(t),
                    owner=owner,
                    description=factory.paragraph(nb_sentences=50),
                    code="".join(choices(string.ascii_lowercase + string.digits, k=6)),
                    no_bots=randint(0, 100),
                    no_players=randint(0, 100),
                    cover_img_url="https://placeimg.com/400/400/any",
                    vid_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                    exp_url=f"https://portal.battlefield.com/experience/rules?playgroundId={uuid4()}",
                    first_published_at=datetime.datetime.now(datetime.timezone.utc),
                )
                cat = choice(cats)
                page.category = cat
                page.tags.add(*choices(tags, k=10)),
                experiences_page.add_child(instance=page)
                experiences_page.save()

            logger.info(
                f"Successfully added {page_count} pages\nTotal Count:- {len(ExperiencePage.objects.all())}"
            )
