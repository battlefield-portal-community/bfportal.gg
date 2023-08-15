from allauth.socialaccount.models import SocialAccount
from rest_framework.renderers import JSONRenderer
from wagtail.api import APIField
from wagtail.api.v2.filters import BaseFilterBackend, FieldsFilter
from wagtail.api.v2.views import BaseAPIViewSet

from .. import serializers
from ..models import Profile


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
        return queryset


class ProfileAPIViewSet(BaseAPIViewSet):
    """User profiles within bfportal.gg."""

    @property
    def default_response_headers(self):
        """Adds cache-control header"""
        headers = BaseAPIViewSet.default_response_headers.fget(self)
        headers["Cache-Control"] = "public, max-age=300"
        return headers

    name = "UsersApi"
    renderer_classes = [JSONRenderer]
    model = Profile
    filter_backends = [UserFilter, FieldsFilter]
    body_fields = [
        "id",
        "type",
        "detail_url",
    ]
    listing_default_fields = ["user"]
    meta_fields = []

    def check_query_parameters(self, queryset):
        """
        Checks if all the parameters are valid,

        Overriden here so that we can send custom params in our requests
        see `UserFilter` class

        """
        pass


Profile.api_fields = [
    APIField("user", serializer=serializers.UserModelSerializer()),
    APIField("liked", serializer=serializers.ExperiencePageSerializerBasic(many=True)),
    APIField("is_mock_user"),
    APIField("hide_username"),
]
