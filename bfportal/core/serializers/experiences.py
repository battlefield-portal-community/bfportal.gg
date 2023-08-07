from rest_framework import serializers
from taggit.serializers import TaggitSerializer, TagListSerializerField

from ..models.experience import ExperiencePage
from .category import ExperiencesCategorySerializer, SubCategoryCategorySerializer


class ExperiencePageSerializer(TaggitSerializer, serializers.ModelSerializer):
    """Serializer for ExperiencePage model."""

    category = ExperiencesCategorySerializer()
    sub_categories = SubCategoryCategorySerializer(many=True)
    tags = TagListSerializerField()
    liked_by = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()

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
            "liked_by",
            "like_count",
            "first_publish",
            "creators",
            "allow_editing",
            "is_mock",
        ]
        depth = 0

    def get_liked_by(self, obj: ExperiencePage):
        """Returns profiles of Users that liked an Experience."""
        from .users import ProfileSerializerNoLikes

        return ProfileSerializerNoLikes(obj.liked_by, many=True).data

    def get_owner(self, obj: ExperiencePage):
        """Serializers owner field with custom Serializer."""
        from .users import UserModelSerializer

        return UserModelSerializer(obj.owner).data


class ExperiencePageSerializerNoLikedBy(
    ExperiencePageSerializer, serializers.ModelSerializer
):
    """Serializer for ExperiencePage but Without Who liked it"""

    liked_by = None

    class Meta:
        model = ExperiencePage
        fields = ExperiencePageSerializer.Meta.fields


class ExperiencePageSerializerBasic(
    ExperiencePageSerializer, serializers.ModelSerializer
):
    """
    Experience Page Serializer that returns only some fields,

    id
    title
    first_publish
    last_published_at
    owner
    like_count
    """

    class Meta:
        model = ExperiencePage
        fields = [
            "id",
            "title",
            "first_publish",
            "last_published_at",
            "owner",
            "like_count",
        ]
