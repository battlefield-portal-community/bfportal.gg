from rest_framework import serializers
from taggit.serializers import TaggitSerializer, TagListSerializerField

from ..models.experience import ExperiencePage
from .category import ExperiencesCategorySerializer, SubCategoryCategorySerializer


class ExperiencePageSerializerNoLikedBy(TaggitSerializer, serializers.ModelSerializer):
    """Serializer for ExperiencePage model."""

    category = ExperiencesCategorySerializer()
    sub_categories = SubCategoryCategorySerializer(many=True)
    tags = TagListSerializerField()

    class Meta:
        model = ExperiencePage
        fields = [
            "featured",
            "description",
            "code",
            "exp_url",
            "tags",
            "vid_url",
            "cover_img_url",
            "no_players",
            "no_bots",
            "category",
            "sub_categories",
            "bugged",
            "broken",
            "xp_farm",
            "first_publish",
            "creators",
            "allow_editing",
            "is_mock",
        ]
        depth = 0
