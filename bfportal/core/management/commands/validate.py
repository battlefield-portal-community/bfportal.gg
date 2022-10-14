import asyncio
from datetime import datetime
from threading import Thread
from urllib.parse import parse_qs, urlsplit  # noqa:  E402

import aiohttp
import requests  # noqa:  E402
from asgiref.sync import sync_to_async
from core.helper import GT_BASE_URL
from core.models import ExperiencePage  # noqa:  E402
from django.core.management import BaseCommand  # noqa:  E402
from loguru import logger


async def fetch(session, page: ExperiencePage, url: str):
    """Checks GT api if an experience is valid or not"""
    async with session.get(url) as response:
        if response.status == 404:
            logger.debug(f"{page} is broken....")
            page.broken = True
        else:
            json: dict = await response.json()
            if json.get("originalPlayground", False):
                if page.broken:
                    logger.debug(f"{page} was broken now fixed....")
                page.broken = False
            else:
                page.broken = True

        await sync_to_async(page.save, thread_sensitive=True)()


async def fetch_all(session, mapping: dict[ExperiencePage, str]):
    """Makes all tasks"""
    tasks = []
    for page, url in mapping.items():
        task = asyncio.create_task(fetch(session, page, url))
        tasks.append(task)
    await asyncio.gather(*tasks)


async def main(mapping: dict[ExperiencePage, str]):
    """Start the validating loop"""
    async with aiohttp.ClientSession() as session:
        await fetch_all(session, mapping)


def start_background_loop(loop: asyncio.AbstractEventLoop) -> None:
    """Used to set event loop"""
    asyncio.set_event_loop(loop)
    loop.run_forever()


class Command(BaseCommand):
    """A command to validate all share codes and playground URL"""

    help = "validates all share codes and playground URL"

    def add_arguments(self, parser):  # noqa: D102
        parser.add_argument("--experiences", action="store_true")

    def handle(self, *args, **options):  # noqa: D102
        if options.get("experiences", None):
            experience: ExperiencePage
            experiences = ExperiencePage.objects.live().public()
            mapping: dict[ExperiencePage, str] = dict()
            for experience in experiences:
                query_string = ""
                if experience.exp_url:
                    parsed_url = urlsplit(experience.exp_url)
                    query_dict = parse_qs(parsed_url.query)
                    if playgroundId := query_dict.get("playgroundId", None):
                        query_string = f"playgroundid={playgroundId[0]}"
                elif experience.code:
                    query_string = f"experiencecode={experience.code}"

                mapping[experience] = GT_BASE_URL.format(query_string)

            loop = asyncio.new_event_loop()
            t = Thread(target=start_background_loop, args=(loop,), daemon=True)
            t.start()
            start_time = datetime.now()
            task = asyncio.run_coroutine_threadsafe(main(mapping), loop)
            task.result()
            exec_time = (datetime.now() - start_time).total_seconds()
            print(f"It took {exec_time:,.2f} seconds to run")
            loop.stop()
