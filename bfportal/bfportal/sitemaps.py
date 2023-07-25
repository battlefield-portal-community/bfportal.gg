from core.helper import user_to_api_response
from core.models import Profile
from django.contrib.sitemaps import Sitemap
from wagtail.contrib.sitemaps.sitemap_generator import Sitemap as WagtailSitemap


class ProfileSitemap(Sitemap):
    """Class that generates sitemap for users."""

    changefreq = "daily"
    priority = 0.5
    protocol = "https"

    def items(self):
        """Return all users that have not hidden their username."""
        return Profile.objects.filter(hide_username=False)

    def location(self, obj):
        """Return the location of the user's profile page."""
        user_data = user_to_api_response(obj.user)
        loc = user_data["id"] if user_data["id"] else user_data["username"]
        return f"/users/{loc}/"


sitemaps = {
    "wagtail": WagtailSitemap,
    "users": ProfileSitemap,
}
