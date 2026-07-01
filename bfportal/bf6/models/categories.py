from core.models.categories import BaseCategory
from wagtail.snippets.models import register_snippet


class ScriptsCategory(BaseCategory):
    """Category for Scripts"""

    class Meta:
        verbose_name = "Scripts Category"
        verbose_name_plural = "Scripts Categories"


class ScriptsSubCategory(BaseCategory):
    """Sub Categories for a Scripts model"""

    class Meta:
        verbose_name = "Scripts Sub Category"
        verbose_name_plural = "Scripts Sub Categories"


register_snippet(ScriptsCategory)
register_snippet(ScriptsSubCategory)
