from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.settings.models import BaseGenericSetting, register_setting


@register_setting
class GenericSystemSettings(BaseGenericSetting):
    """
    Generic settings for bfportal,

    settings available,
    need_login_to_view_profile: bool
    """

    need_login_to_view_profile = models.BooleanField(default=False)

    panels = [
        FieldPanel("need_login_to_view_profile"),
    ]
