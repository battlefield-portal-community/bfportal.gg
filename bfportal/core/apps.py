from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Config Class for Core app"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        """Called as soon as config for core app is set"""
        from . import signal_recivers  # noqa: F401
