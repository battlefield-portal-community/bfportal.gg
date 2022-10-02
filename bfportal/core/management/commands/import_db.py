import dataclasses
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import django.core.exceptions
from core.models import ExperiencePage, ExperiencesCategory, ExperiencesPage
from core.utils.helper import unique_slug_generator
from django.contrib.auth.models import User
from django.core.management import BaseCommand
from loguru import logger


@dataclass()
class DBRow:
    """DataClass that represents a row in DB"""

    experience_name: str
    verified: bool
    featured: bool
    trending: bool
    official: bool
    portal_jam: bool
    last_edited_time: str
    owner: str | None
    type: str
    number_players: int
    number_pvp_ai: int
    number_pve_ai: int
    tags: list[str, ...] | list
    experience_code: str | None
    experience_edit_url: str | None
    created_date: str
    image_link: str
    video_link: str | None
    description: str


class Command(BaseCommand):
    """A command to get all tags from GameTools used for internal testing"""

    help = "Imports data from db.csv"

    def add_arguments(self, parser):  # noqa: D102
        parser.add_argument("link_to_json", metavar="link", type=str, nargs="+")

    def handle(self, *args, **options):  # noqa: D102
        db_json_file = Path(__file__).parent / "db.json"
        with db_json_file.open() as db_file:
            json_db = json.load(db_file)
        su = User.objects.filter(is_superuser=True).first()
        for json_row in json_db:

            row = DBRow(**json_row)
            if row.type == "Prefabs":
                row.type = "Prefab"
            elif row.type == "Coop":
                row.type = "co-op"
            elif row.type == "Competitive":
                row.type = "Multiplayer"
            try:
                if not ExperiencePage.objects.filter(
                    title__iexact=row.experience_name
                ).exists():
                    page = ExperiencePage(
                        title=row.experience_name,
                        featured=row.featured,
                        trending=row.trending,
                        description=row.description,
                        code=row.experience_code
                        if len(row.experience_code) == 6
                        else "",
                        exp_url=row.experience_edit_url,
                        vid_url=row.video_link,
                        cover_img_url=row.image_link,
                        no_players=row.number_players,
                        no_bots=row.number_pve_ai + row.number_pvp_ai,
                        owner=su,
                    )
                    page.slug = unique_slug_generator(page)
                    if (
                        cat := ExperiencesCategory.objects.filter(
                            name__icontains=row.type
                        )
                    ).exists():
                        page.category = cat[0]
                    else:
                        page.category = ExperiencesCategory.objects.first()

                    page.first_published_at = datetime.strptime(
                        row.created_date, "%B %d %Y %I %S %p"
                    ).replace(tzinfo=timezone.utc)
                    if row.last_edited_time:
                        page.last_published_at = datetime.strptime(
                            row.last_edited_time, "%B %d %Y %I %S %p"
                        ).replace(tzinfo=timezone.utc)
                    page.tags.add(*row.tags)
                    exps_page = ExperiencesPage.objects.first()
                    exps_page.add_child(instance=page)
                    exps_page.save()
                else:
                    logger.debug(f"{row.experience_name} exists... skipping...")
            except django.core.exceptions.ValidationError as e:
                logger.critical(f"failed on {dataclasses.asdict(row)}")
                logger.critical(e)
