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

    # Tabs shown at the top of the listing page. Add an entry here to add a tab;
    # the template distributes them evenly and no other change is needed.
    tabs = [
        {"key": "snippets", "label": "SNIPPETS", "href": "/scripts/snippets/"},
        {"key": "experiences", "label": "EXPERIENCES", "href": "/scripts/experiences/"},
    ]

    def get_context(self, request: HttpRequest, *args, **kwargs):  # noqa: D102
        context = super().get_context(request, *args, **kwargs)
        context["script_tabs"] = self.tabs
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

    @route(r"^$")
    @route(r"^snippets/$")
    def list_snippets(self, request: HttpRequest):
        """Render the scripts listing page with the snippets tab active."""
        context = self.get_context(request)
        context["active_tab"] = "snippets"
        context["snippets"] = pagination_wrapper(
            request,
            SnippetPage.objects.live().public().order_by("-first_published_at"),
        )
        return TemplateResponse(request, self.get_template(request), context)

    @route(r"^experiences/$")
    def list_experiences(self, request: HttpRequest):
        """Render the scripts listing page with the experiences tab active."""
        context = self.get_context(request)
        context["active_tab"] = "experiences"
        return TemplateResponse(request, self.get_template(request), context)
