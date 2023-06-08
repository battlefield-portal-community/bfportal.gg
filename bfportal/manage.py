#!/usr/bin/env python
import os
import sys
import warnings

from dotenv import load_dotenv

load_dotenv()

from bfportal.settings.base import setup_logging  # noqa: E402

setup_logging()

if __name__ == "__main__":
    with warnings.catch_warnings():
        from wagtail.utils.deprecation import RemovedInWagtail50Warning

        warnings.filterwarnings("ignore", category=RemovedInWagtail50Warning)
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bfportal.settings.dev")
        from django.core.management import execute_from_command_line

        execute_from_command_line(sys.argv)
