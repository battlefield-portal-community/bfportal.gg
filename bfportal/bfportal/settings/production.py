import os

from .base import *

DEBUG = True if os.environ.get("DEBUG", "False") == "True" else False
SECRET_KEY = os.environ.get("PRODUCTION_KEY")
ALLOWED_HOSTS = ["*"]  # todo add aws host soon 😊

try:
    from .local import *
except ImportError:
    pass
