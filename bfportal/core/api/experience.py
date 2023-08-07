from rest_framework.renderers import JSONRenderer
from wagtail.api import APIField
from wagtail.api.v2.views import PagesAPIViewSet

from .. import serializers
from ..models import ExperiencePage


class ExperiencePageAPIViewSet(PagesAPIViewSet):
    """
    ViewSet used to define how the api for ExperiencePage will work.

    # todo: serialize all field
    """

    renderer_classes = [JSONRenderer]
    model = ExperiencePage


ExperiencePage.api_fields = [
    APIField("owner", serializer=serializers.UserModelSerializer()),
    APIField("featured"),
    APIField("description"),
    APIField("code"),
    APIField("exp_url"),
    APIField("tags"),
    APIField("vid_url"),
    APIField("cover_img_url"),
    APIField("no_players"),
    APIField("no_bots"),
    APIField("category", serializer=serializers.ExperiencesCategorySerializer()),
    APIField(
        "sub_categories",
        serializer=serializers.SubCategoryCategorySerializer(many=True),
    ),
    APIField("bugged"),
    APIField("broken"),
    APIField("xp_farm"),
    APIField("first_publish"),
    APIField("liked_by", serializer=serializers.ProfileSerializerNoLikes(many=True)),
    APIField("creators", serializer=serializers.UserModelSerializer(many=True)),
    APIField("allow_editing"),
    APIField("is_mock"),
]
