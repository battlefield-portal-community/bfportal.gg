from .base import *

DEBUG = False
SECRET_KEY = os.environ.get("PRODUCTION_KEY")
ALLOWED_HOSTS = ["*"]  # todo add aws host soon 😊

try:
    from .local import *
except ImportError:
    pass
