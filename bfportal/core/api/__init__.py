from wagtail.api.v2.router import WagtailAPIRouter

from .experience import ExperiencePageAPIViewSet

api_router = WagtailAPIRouter("wagtailapi")
api_router.register_endpoint("experiences", ExperiencePageAPIViewSet)
