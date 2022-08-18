import os

from .base import *  # noqa: F403,F401

DEBUG = True if os.environ.get("DEBUG", "False") == "True" else False
SECRET_KEY = os.environ.get("PRODUCTION_KEY")
ALLOWED_HOSTS = [
    os.environ.get("PRODUCTION_HOST"),
    "localhost",
]

try:
    from .local import *  # noqa: F403,F401
except ImportError:
    pass
