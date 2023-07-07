import string
from datetime import datetime
from random import choice, choices, randint
from uuid import uuid4

from allauth.socialaccount.models import SocialAccount
from core.helper import get_tags_from_gt_api
from core.models import ExperiencePage, ExperiencesCategory, ExperiencesPage
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.utils.text import slugify
from faker import Faker
from loguru import logger
from snowflake import SnowflakeGenerator


class Command(BaseCommand):
    """A command that generates fake data to populate experiences in Database"""

    help = "Generates fake data"

    def add_arguments(self, parser):  # noqa: D102
        parser.add_argument(
            "-u",
            "--users",
            type=int,
            help="Generates Fake Users",
            nargs="?",
            const=50,
        )
        parser.add_argument(
            "-e",
            "--experiences",
            type=int,
            help="Generates Fake Experience pages",
            nargs="?",
            const=50,
        )

    def handle(self, *args, **options):
        """Handler for command, handles the generation of data"""
        if not settings.DEBUG:
            logger.critical("MOCK COMMAND CAN ONLY BE USED WHEN DEBUG IS SET TO TRUE")
            return

        map_images = {
            "MP_Harbor": "https://eaassets-a.akamaihd.net/battlelog/battlebinary/gamedata/kingston/60/b4/Map_Art_BFBC2_AH_L-60b49760.png",  # noqa: E501
            "MP_LightHouse": "https://eaassets-a.akamaihd.net/battlelog/battlebinary/gamedata/kingston/60/03/Map_Art_BFBC2_VP_L-600385e2.png",  # noqa: E501
            "MP_Frost": "https://eaassets-a.akamaihd.net/battlelog/battlebinary/gamedata/kingston/25/59/Map_Art_BF1942_BB_L-2559980c.png",  # noqa: E501
            "MP_Oasis": "https://eaassets-a.akamaihd.net/battlelog/battlebinary/gamedata/kingston/d7/d3/Map_Art_BF1942_EA_L-d7d3186f.png",  # noqa: E501
            "MP_Rural": "https://eaassets-a.akamaihd.net/battlelog/battlebinary/gamedata/kingston/df/50/Map_Art_BF3_CB_L-df505a1f.png",  # noqa: E501
            "MP_Port": "https://eaassets-a.akamaihd.net/battlelog/battlebinary/gamedata/kingston/41/a1/Map_Art_BF3_NC_L-41a1e94f.png",  # noqa: E501
            "MP_Orbital": "https://eaassets-a.akamaihd.net/battlelog/battlebinary/gamedata/kingston/d1/5a/Map_Art_BF2042_ORB_L-d15a84f6.png",  # noqa: E501
            "MP_Hourglass": "https://eaassets-a.akamaihd.net/battlelog/battlebinary/gamedata/kingston/95/35/Map_Art_BF2042_HG_L-9535453c.png",  # noqa: E501
            "MP_Kaleidoscope": "https://eaassets-a.akamaihd.net/battlelog/battlebinary/gamedata/kingston/6b/a7/Map_Art_BF2042_KS_L-6ba702e0.png",  # noqa: E501
            "MP_Irreversible": "https://eaassets-a.akamaihd.net/battlelog/battlebinary/gamedata/kingston/19/ee/Map_Art_BF2042_IRR_L-19eeef98.png",  # noqa: E501
            "MP_Discarded": "https://eaassets-a.akamaihd.net/battlelog/battlebinary/gamedata/kingston/76/46/Map_Art_BF2042_DIS_L-764694ca.png",  # noqa: E501
            "MP_LongHaul": "https://eaassets-a.akamaihd.net/battlelog/battlebinary/gamedata/kingston/22/b3/Map_Art_BF2042_LH_L-22b32735.png",  # noqa: E501
            "MP_TheWall": "https://eaassets-a.akamaihd.net/battlelog/battlebinary/gamedata/kingston/ad/09/Map_Art_BF2042_TW_L-ad09f15f.png",  # noqa: E501
            "MP_Ridge": "https://eaassets-a.akamaihd.net/battlelog/battlebinary/gamedata/kingston/66/e8/Map_Art_BF2042_RID_L-66e845a2.png",  # noqa: E501
            "MP_Drained": "https://eaassets-a.akamaihd.net/battlelog/battlebinary/gamedata/kingston/d7/5f/Map_Art_BF2042_DRA_L-d75f98a0.png",  # noqa: E501
        }
        map_images = list(map_images.values())
        if number_of_users := options.get("users", False):
            self.stdout.write(f"Generating {number_of_users} Users")
            User = get_user_model()
            snowflake_factory = SnowflakeGenerator(1)  # find what the 1 is for :)
            Faker.seed("bfportal.gg")  # make sure we get the same data every time
            faker_factory = Faker()
            for user in range(number_of_users):
                username = faker_factory.unique.first_name()
                # check if user already exists
                if User.objects.filter(username=username).exists():
                    self.stdout.write(f"User with {username} exists skipping...")
                    # todo: discuss if how to handle username collision
                    # username = username + str(datetime.timestamp(datetime.utcnow()))
                    # add timestamp to username to make it unique
                user_attributes = {
                    "username": username,
                    "first_name": username,
                    "last_name": faker_factory.unique.last_name(),
                    "email": f"{username}@fake.gg",
                    "password": "fake_user",
                }
                socialaccount_extra_data = {
                    "id": str(next(snowflake_factory)),
                    "username": username,
                    "global_name": None,
                    "display_name": None,
                    "avatar": None,
                    "discriminator": "0",
                    "public_flags": 4194432,
                    "flags": 4194432,
                    "banner": None,
                    "banner_color": "#292b2f",
                    "accent_color": 2698031,
                    "locale": "en-US",
                    "mfa_enabled": faker_factory.pybool(),
                    "premium_type": 0,
                    "avatar_decoration": None,
                    "email": user_attributes["email"],
                    "verified": faker_factory.pybool(),
                }
                user = User(**user_attributes)
                user._mock_user = True
                user.save()  # we need to save as user id is required by Allauth

                social_account = SocialAccount()
                social_account.extra_data = socialaccount_extra_data
                social_account.user_id = user.id
                social_account.uid = socialaccount_extra_data["id"]
                social_account.save()

                user.socialaccount_set.add(social_account)
                user.save()

        if page_count := options.get("experiences", False):
            factory = Faker()
            cats = ExperiencesCategory.objects.all()
            owner = [
                user for user in get_user_model().objects.all() if not user.is_superuser
            ]
            tags = get_tags_from_gt_api()
            experiences_page = ExperiencesPage.objects.first()
            self.stdout.write(
                f"Generating {page_count} Experience Pages, this may take a while..."
            )
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
                    owner=choice(owner),
                    description=factory.paragraph(nb_sentences=50),
                    code="".join(choices(string.ascii_lowercase + string.digits, k=6)),
                    no_bots=randint(0, 100),
                    no_players=randint(0, 100),
                    cover_img_url=choice(map_images),
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
