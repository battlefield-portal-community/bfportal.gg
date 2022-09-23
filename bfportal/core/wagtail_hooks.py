from django.http import HttpRequest
from django.utils.html import format_html
from loguru import logger
from wagtail import hooks
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from .models import ExperiencePage


class ExperiencePageAdmin(ModelAdmin):
    """Controls how 'Experience Pages' menu items works and looks"""

    model = ExperiencePage
    menu_order = 1
    list_display = ("title", "get_owner", "live", "last_updated_at")
    search_fields = ("title",)

    def get_owner(self, page: ExperiencePage):
        """Returns html formatted string containing avatar and username."""
        if social_account := page.owner.socialaccount_set.first():
            extra_data = social_account.extra_data
            if extra_data["avatar"]:
                src = f"https://cdn.discordapp.com/avatars/{extra_data['id']}/{extra_data['avatar']}.png"
            else:
                src = ""
        else:
            src = ""
        return format_html(
            """
            <div style="display:flex;align-items:center;column-gap:5px" >
                <img src="{}", alt=" " width=20 height=20 style="border-radius:100%" >
                <span>{}</span>
            </div>
            """,
            src,
            page.owner,
        )

    get_owner.short_description = "Owner"
    get_owner.admin_order_field = "owner"

    def last_updated_at(self, page: ExperiencePage):
        """Returns the last_published_at, else returns first_published_at."""
        if not page.last_published_at:
            return page.first_published_at
        return page.last_published_at

    def get_queryset(self, request):
        """Returns the queryset that contains all ExperiencePages by the request.user."""
        qs = super().get_queryset(request)
        # Only show people managed by the current user
        if (
            request.user.is_superuser
            or request.user.groups.filter(name="Moderators").exists()
        ):
            return qs
        return qs.filter(owner=request.user)


@hooks.register("construct_main_menu")
def only_show_experiences_pages_item(request: HttpRequest, menu_items):
    """Returns only the Experience Pages menu items for a non superuser"""
    logger.debug([item.name for item in menu_items])
    if request.user.is_superuser:
        return menu_items
    elif request.user.groups.filter(name="Moderators").exists():
        menu_items[:] = [item for item in menu_items if item.name != "explorer"]
    else:
        menu_items[:] = [item for item in menu_items if item.name == "experience-pages"]

    return menu_items


modeladmin_register(ExperiencePageAdmin)
