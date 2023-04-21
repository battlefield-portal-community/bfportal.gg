"""
WSGI config for bfportal project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os
import warnings

from django.core.wsgi import get_wsgi_application
from dotenv import load_dotenv

load_dotenv()


def init_project():
    """Initialize the project

    Used to load .env file and set project specific settings
    """
    from loguru import logger

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bfportal.settings.production")
    logger.info(".env loaded")


with warnings.catch_warnings():
    from wagtail.utils.deprecation import RemovedInWagtail50Warning

    warnings.filterwarnings(
        "ignore", category=RemovedInWagtail50Warning
    )  # supress only wagtail warnings
    init_project()
    application = get_wsgi_application()
