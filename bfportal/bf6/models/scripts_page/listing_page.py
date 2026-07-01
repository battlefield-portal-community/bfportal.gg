from bf6.models.scripts_page.snippets import SnippetPage
from core.models.helper import pagination_wrapper
from core.models.pages import CustomBasePage
from django.http import HttpRequest
from django.template.response import TemplateResponse
from wagtail.contrib.routable_page.models import RoutablePageMixin, route


class ScriptsListingPage(RoutablePageMixin, CustomBasePage):
    """Class defining page that lists all scripts"""

    max_count = 1
    parent_page_types = ["bf6.BF6HomePage"]
    subpage_types = ["bf6.SnippetPage", "core.BlogPage"]

    def get_context(self, request, *args, **kwargs):
        """Adding custom stuff to our context."""
        context = super().get_context(request, *args, **kwargs)
        # Get all posts
        context["posts"] = pagination_wrapper(
            request,
            SnippetPage.objects.live().public().order_by("-first_published_at"),
        )
        return context

    @route(r"^featured/$")
    def featured_experiences(self, request: HttpRequest):  # noqa: D102
        return TemplateResponse(
            request,
            self.get_template(request),
            {
                "posts": SnippetPage.objects.live()
                .filter(featured__exact=True)
                .order_by("-first_published_at"),
            },
        )
