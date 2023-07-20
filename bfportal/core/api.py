from allauth.socialaccount.models import SocialAccount
from rest_framework.filters import BaseFilterBackend
from rest_framework.renderers import JSONRenderer
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.api.v2.views import BaseAPIViewSet, PagesAPIViewSet

from .models import ExperiencePage, Profile


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
        "broken",
        "like_count",
        "exp_creators",
    ]
    listing_default_fields = body_fields


class UserFilter(BaseFilterBackend):
    """
    Filter used on the queryset of Users API

    Only cares for `username` and `uid` field
    """

    def filter_queryset(self, request, queryset, view):
        """
        The actual function that does the filtering,

        tbh I am not confident if I implemented the best solution
        especially in the part where we filter based on `uid`,
        this filtering function maybe be a fucking performance tanker
        """
        if uid := request.GET.get("uid", None):
            if social := SocialAccount.objects.filter(
                provider="discord", uid=uid
            ).first():
                return queryset.filter(user=social.user)
        if username := request.GET.get("username", None):
            return queryset.filter(user__username__icontains=username)
        return queryset.none()


class UsersAPIViewSet(BaseAPIViewSet):
    """View for Users API."""

    model = Profile
    renderer_classes = [JSONRenderer]
    body_fields = ["username", "uid"]
    listing_default_fields = body_fields
    filter_backends = [UserFilter]

    def check_query_parameters(self, queryset):
        """Defined to override the default behaviour

        This might fuck something I don't know, only time will tell
        currently because of one can pass any fucking param in GET request
        """
        pass  # allow all as filter is in our hand


api_router = WagtailAPIRouter("wagtailapi")
api_router.register_endpoint("experiences", ExperiencePageAPIViewSet)
api_router.register_endpoint("users", UsersAPIViewSet)
