from rest_framework import serializers

from ..models.categories import BaseCategory, ExperiencesCategory, SubCategory

__all__ = ["ExperiencesCategorySerializer", "SubCategoryCategorySerializer"]


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


class SubCategoryCategorySerializer(BaseCategorySerializer):
    """Serializer for SubCategory."""

    class Meta:
        model = SubCategory
        exclude = BaseCategorySerializer.Meta.exclude
