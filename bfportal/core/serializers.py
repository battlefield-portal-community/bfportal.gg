from rest_framework import serializers

from .models.categories import BaseCategory, ExperiencesCategory


class BaseCategorySerializer(serializers.ModelSerializer):
    """Serializer for BaseCategory."""

    class Meta:
        model = BaseCategory
        exclude = ["icon"]  # todo: serialize svg field


class ExperiencesCategorySerializer(BaseCategorySerializer):
    """Serializer for ExperiencesCategory."""

    class Meta:
        model = ExperiencesCategory
        exclude = BaseCategorySerializer.Meta.exclude
