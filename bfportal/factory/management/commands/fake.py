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
