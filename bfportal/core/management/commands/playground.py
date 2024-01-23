from pathlib import Path

from django.core.management import BaseCommand
from loguru import logger


class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.debug("This is a command to be used as a playground")
