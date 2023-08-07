from wagtail.api.v2.router import WagtailAPIRouter

from .experience import ExperiencePageAPIViewSet
from .users import ProfileAPIViewSet

api_router = WagtailAPIRouter("wagtailapi")
api_router.register_endpoint("experiences", ExperiencePageAPIViewSet)
api_router.register_endpoint("users", ProfileAPIViewSet)
