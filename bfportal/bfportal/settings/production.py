import os

from loguru import logger

from .base import *  # noqa: F403,F401

DEBUG = True if os.environ.get("DEBUG", "False") == "True" else False
SECRET_KEY = os.environ.get("PRODUCTION_KEY")
ALLOWED_HOSTS = os.environ.get("PRODUCTION_HOST").split(",")
ALLOWED_HOSTS.append("localhost")
CSRF_TRUSTED_ORIGINS = ["https://*.bfportal.gg/"]
logger.debug(f"Allowed Hosts {ALLOWED_HOSTS}")

try:
    from .local import *  # noqa: F403,F401
except ImportError:
    pass
