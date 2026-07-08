import sys
from datetime import datetime, timezone
from random import choice, randint, sample

from bf6.models import ScriptsCategory, ScriptsListingPage, SnippetPage
from core.management.commands.mock import ensure_mock_users
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand, call_command
from django.utils.text import slugify
from faker import Faker
from loguru import logger
from mdgen import MarkdownPostProvider

User = get_user_model()

# A few sample Portal script bodies to drop into the `code` field of a snippet.
SAMPLE_SCRIPTS = [
    "mod.OnPlayerDeployed((player) => {\n    player.SetMaxHealth(150);\n});",
    "mod.OnPlayerEarnedKill((killer, victim) => {\n    killer.Heal(25);\n});",
    'mod.OnGameModeStarted(() => {\n    ui.ShowNotification("Custom rules loaded!");\n});',
    "mod.OnPlayerJoinGame((player) => {\n    player.SetInventoryMagazineAmmo(1.0);\n});",
    "mod.OnTimeLimitReached(() => {\n    mod.EndRound(mod.GetTargetTeam());\n});",
]


class Command(BaseCommand):
    """A command that generates fake SnippetPages to populate the bf6 scripts listing."""

    help = "Generates fake snippet data"

    def add_arguments(self, parser):  # noqa: D102
        parser.add_argument(
            "-s",
            "--snippets",
            type=int,
            help="Generates Fake Snippet pages",
            nargs="?",
            const=50,
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Removes all mock snippets from the database",
        )
        parser.add_argument(
            "--noregen",
            action="store_true",
            help="Does not regenerate mock snippets if they already exist",
        )

    def handle(self, *args, **options):
        """Handler for command, handles the generation of snippet data"""
        if len(sys.argv) <= 2:
            self.print_help("manage.py", "mock_snippets")
            return
        if not settings.DEBUG:
            logger.critical(
                "MOCK_SNIPPETS COMMAND CAN ONLY BE USED WHEN DEBUG IS SET TO TRUE"
            )
            return
        if options.get("noregen", False) and options.get("clear", False):
            logger.critical("Cannot use --noregen and --clear together")
            self.stdout.write("Cannot use --noregen and --clear together")
            return
        if options.get("noregen", False):
            #  only generate data if there are no mock snippets in the database
            if not SnippetPage.objects.filter(is_mock=True).exists():
                call_command(
                    "mock_snippets",
                    "-s",
                    options.get("snippets", 10),
                )
                return
            self.stdout.write(
                "Mock snippets already exist in the database.. skipping generation"
            )
            return

        if options.get("clear", False):
            mock_snippets = SnippetPage.objects.filter(is_mock=True)
            self.stdout.write(f"Deleting {len(mock_snippets)} snippets....")
            mock_snippets.delete()
            self.stdout.write("Deleted...")
            return

        Faker.seed("bfportal.gg")  # make sure we get the same data every time
        faker_factory = Faker()
        faker_factory.add_provider(MarkdownPostProvider)

        if page_count := options.get("snippets", False):
            listing_page = ScriptsListingPage.objects.first()
            if listing_page is None:
                logger.critical(
                    "No ScriptsListingPage found, cannot generate snippets. "
                    "Create one in the wagtail admin first."
                )
                return

            cats = list(ScriptsCategory.objects.all())
            owners = ensure_mock_users(50)
            self.stdout.write(
                f"Generating {page_count} Snippet Pages, this may take a while..."
            )
            for _ in range(page_count):
                title = faker_factory.sentence(nb_words=randint(3, 7))
                owner = choice(owners)
                page = SnippetPage(
                    title=title,
                    slug=slugify(title),
                    owner=owner,
                    description=faker_factory.post(size="large"),
                    code=choice(SAMPLE_SCRIPTS),
                    vid_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                    first_published_at=datetime.now(timezone.utc),
                )
                if cats:
                    page.category = choice(cats)

                page.is_mock = True
                page.featured = faker_factory.pybool()
                page.trending = faker_factory.pybool()
                page.allow_editing = faker_factory.pybool()
                listing_page.add_child(instance=page)
                listing_page.save()

                # add likes
                liked_by_candidates = [user for user in owners if user != owner]
                number_to_select_for_likes = (
                    _n if (_n := len(liked_by_candidates)) < 5 else randint(5, _n)
                )
                liked_by = sample(liked_by_candidates, number_to_select_for_likes)
                for user in liked_by:
                    page.liked_by.add(user.profile)

                for user in liked_by[0 : randint(0, 4)]:
                    page.creators.add(user)

                page.save()
