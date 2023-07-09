"""
WSGI config for bfportal project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os
import warnings

from loguru import logger


def init_project():
    """Initialize the project"""
    logger.info("project loaded")


def init_wsgi():
    """Initialize the WSGI

    Used to load .env file and set project specific settings
    """
    global application
    with warnings.catch_warnings():
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bfportal.settings.production")
        from django.core.wsgi import get_wsgi_application
        from wagtail.utils.deprecation import RemovedInWagtail60Warning

        warnings.filterwarnings(
            "ignore", category=RemovedInWagtail60Warning
        )  # supress only wagtail warnings
        application = get_wsgi_application()


application = None
init_project()
init_wsgi()
