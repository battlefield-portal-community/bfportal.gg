#!/usr/bin/env python
import os
import sys

from dotenv import load_dotenv
from loguru import logger

load_dotenv()


if __name__ == "__main__":
    logger.remove()
    logger.add(
        sys.stdout,
        colorize=True,
        format="[ <lr>bfportal</> ]"
        "[<b><fg #3b3b3b>{level: ^8}</></>]"
        "[{name}.{function}:{line}]"
        "[ {message} ]",
        level="DEBUG",
    )
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bfportal.settings.dev")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
