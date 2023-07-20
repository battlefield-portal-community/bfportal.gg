from rest_framework.renderers import JSONRenderer
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.api.v2.views import PagesAPIViewSet

from .models import ExperiencePage


class ExperiencePageAPIViewSet(PagesAPIViewSet):
    """
    ViewSet used to define how the api for ExperiencePage will work.

    # todo: serialize all field
    """

    renderer_classes = [JSONRenderer]
    model = ExperiencePage


api_router = WagtailAPIRouter("wagtailapi")
api_router.register_endpoint("experiences", ExperiencePageAPIViewSet)
