from rest_framework.renderers import JSONRenderer
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.api.v2.views import BaseAPIViewSet, PagesAPIViewSet

from .models import ExperiencePage


class ExperiencePageAPIViewSet(BaseAPIViewSet):
    """Class that defines how page api works."""

    renderer_classes = [JSONRenderer]
    model = ExperiencePage
    filter_backends = PagesAPIViewSet.filter_backends
    body_fields = [
        "url",
        "id",
        "full_url",
        "title",
        "description",
        "cover_img_url",
        "code",
        "exp_url",
        "featured",
        "bugged",
        "xp_farm",
        "like_count",
        "exp_creators",
    ]
    listing_default_fields = body_fields


api_router = WagtailAPIRouter("wagtailapi")
api_router.register_endpoint("experiences", ExperiencePageAPIViewSet)
