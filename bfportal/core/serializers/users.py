from django.contrib.auth import get_user_model
from rest_framework import serializers

from ..models.experience import ExperiencePage
from ..models.users import Profile
from .experiences import ExperiencePageSerializerNoLikedBy


class LikedSerializer(ExperiencePageSerializerNoLikedBy, serializers.ModelSerializer):
    """Serializer for Liked in a profile."""

    class Meta:
        model = ExperiencePage
        fields = [
            field
            for field in ExperiencePageSerializerNoLikedBy.Meta.fields
            if field != "liked_by"
        ]
        depth = 0


class UserModelSerializer(serializers.ModelSerializer):
    """Serializer for User model."""

    social_account = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "social_account",
        ]
        depth = 1

    def get_social_account(self, obj):
        """Adds social account info for a User."""
        if providers := obj.socialaccount_set.all():
            return {provider.provider: provider.extra_data for provider in providers}
        # no provider internal account
        return {}


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for Profile model."""

    user = UserModelSerializer()
    liked = LikedSerializer(many=True)

    class Meta:
        model = Profile
        fields = "__all__"
        depth = 0


class ProfileSerializerNoLikes(ProfileSerializer, serializers.ModelSerializer):
    """Serializer for Profile model without likes."""

    liked = None

    class Meta:
        model = Profile
        exclude = ["liked"]
