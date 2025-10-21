from core.models.pages import CustomBasePage
from wagtail.contrib.routable_page.models import RoutablePageMixin


class BF6HomePage(RoutablePageMixin, CustomBasePage):
    """Home Page model for BF6"""

    max_count = 1
    parent_page_types = ["wagtailcore.Page"]
    template = "bf6/home_page.html"
