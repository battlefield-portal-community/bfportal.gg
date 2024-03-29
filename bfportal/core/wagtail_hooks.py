from django.http import HttpRequest
from django.utils.html import format_html
from wagtail import hooks
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from .models import DiscordScheduledEvent, ExperiencePage, Profile


class ExperiencePageAdmin(ModelAdmin):
    """Controls how 'Experience Pages' menu items works and looks"""

    model = ExperiencePage
    menu_order = 1
    list_display = (
        "title",
        "get_owner",
        "live",
        "last_updated_at",
        "get_bugged_reports",
        "get_broken_reports",
        "get_xp_farm_reports",
    )
    list_filter = (
        "trending",
        "bugged",
        "broken",
        "xp_farm",
        "category",
        "sub_categories",
        "tags",
    )
    search_fields = ("title", "code")

    def get_owner(self, page: ExperiencePage):
        """Returns html formatted string containing avatar and username."""
        src = ""
        if socialaccount_set := page.owner.socialaccount_set:
            if social_account := socialaccount_set.first():
                extra_data = social_account.extra_data
                if extra_data["avatar"]:
                    src = f"https://cdn.discordapp.com/avatars/{extra_data['id']}/{extra_data['avatar']}.png"

        return format_html(
            """
            <div style="display:flex;align-items:center;column-gap:5px;overflow: hidden;" >
                <img src="{}", alt=" " width=20 height=20 style="border-radius:100%" onerror="this.hidden=true" >
                <span style="flex-shrink:0">{}</span>
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

    def get_bugged_reports(self, page: ExperiencePage):
        """Returns the amount of bugged reports"""
        return page.bugged_report.all().count()

    get_bugged_reports.short_description = "Bug Report Count"

    def get_broken_reports(self, page: ExperiencePage):
        """Returns the amount of broken reports"""
        return page.broken_report.all().count()

    get_broken_reports.short_description = "Broken Report Count"

    def get_xp_farm_reports(self, page: ExperiencePage):
        """Returns the amount of XP FARM reports"""
        return page.broken_report.all().count()

    get_xp_farm_reports.short_description = "XP Farm Report Count"

    def get_queryset(self, request):
        """Returns the queryset that contains all ExperiencePages by the request.user."""
        qs = super().get_queryset(request)
        # Only show people managed by the current user
        if (
            request.user.is_superuser
            or request.user.groups.filter(name="Moderators").exists()
        ):
            return qs.live().public().order_by("-first_published_at")
        return (
            qs.filter(owner=request.user)
            .live()
            .public()
            .order_by("-first_published_at")
        )


class ProfileAdmin(ModelAdmin):
    """Controls how 'Profile' menu items works and looks"""

    model = Profile
    menu_order = 2
    list_display = ("username",)
    search_fields = ("user__username",)

    def username(self, profile: Profile):  # noqa: D102
        return profile.user.username

    def get_queryset(self, request: HttpRequest):  # noqa: D102
        if request.user.is_superuser or request.user.groups.filter(
            name__istartswith="mod"
        ):
            return Profile.objects.all()
        else:
            return request.user.profile


class DiscordScheduledEventsAdminPage(ModelAdmin):
    """Class that controls how the DiscordScheduledEvents show up in admin"""

    model = DiscordScheduledEvent
    menu_order = 3

    list_display = ("title",)
    list_filter = ("server_id",)
    search_fields = ("title", "server_id", "event_id")


@hooks.register("construct_main_menu")
def only_show_experiences_pages_item(request: HttpRequest, menu_items):
    """Returns only the Experience Pages menu items for a non superuser"""
    # from loguru import logger
    #
    # logger.debug([item.name for item in menu_items])
    if request.user.is_superuser:
        return menu_items
    elif request.user.groups.filter(name="Moderators").exists():
        return [item for item in menu_items if item.name != "explorer"]
    else:
        return [item for item in menu_items if item.name in ["experience-pages"]]


modeladmin_register(ProfileAdmin)
modeladmin_register(ExperiencePageAdmin)
modeladmin_register(DiscordScheduledEventsAdminPage)
