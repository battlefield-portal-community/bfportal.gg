from urllib.parse import parse_qs, urlsplit  # noqa:  E402

import requests  # noqa:  E402
from core.models import ExperiencePage  # noqa:  E402
from django.core.management import BaseCommand  # noqa:  E402


def request_response_handler(response, *args, **kwargs):
    """Async callback for response"""
    print(response)


def exception_handler(*args):
    """Async callback for error handling"""
    print(args)


class Command(BaseCommand):
    """A command to validate all share codes and playground URL"""

    help = "validates all share codes and playground URL"

    def handle(self, *args, **options):  # noqa: D102
        experiences = ExperiencePage.objects.live().public()
        urls = []
        experience: ExperiencePage
        for experience in experiences:
            base_url = "https://api.gametools.network/bf2042/playground/?{}&blockydata=false&lang=en-us"
            if experience.exp_url:
                parsed_url = urlsplit(experience.exp_url)
                query_dict = parse_qs(parsed_url.query)
                if playgroundId := query_dict.get("playgroundId", None):
                    urls.append(base_url.format(f"playgroundid={playgroundId[0]}"))
            elif experience.code:
                urls.append(base_url.format(f"experiencecode={experience.code}"))
