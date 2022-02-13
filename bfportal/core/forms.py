from django import forms
from core.models import ExperiencePage, ExperiencesCategory

from loguru import logger


class ExperiencePageForm(forms.ModelForm):
    # categories = forms.ModelMultipleChoiceField(
    #     queryset=ExperiencesCategory.objects.all(),
    #     help_text="Choose a Category for your experience",
    #     required=False
    # )

    class Meta:
        model = ExperiencePage
        exclude = ['featured']
        fields = [
            "title",
            "description",
            "categories",
            "exp_url",
            "code",
            "tags",
            "no_players",
            "no_bots",
            "cover_img_url",
            "vid_url",
        ]

    field_order = [
        "exp_url",
        "title",
        "description",
        "code",
        "tags",
        "no_players",
        "no_bots",
        "cover_img_url",
        "vid_url",
        "categories",
    ]

    def clean_categories(self):
        if len(self.cleaned_data["categories"]) > 1:
            raise forms.ValidationError("Select no more than 1.")
        elif len(self.cleaned_data["categories"]) == 0:
            raise forms.ValidationError("Select at least one category")
        return self.cleaned_data["categories"]
