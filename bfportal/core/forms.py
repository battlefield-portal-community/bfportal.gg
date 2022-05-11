from django import forms

from core.models import ExperiencePage


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
        "categories",
        "exp_url",
        "title",
        "description",
        "code",
        "tags",
        "no_players",
        "no_bots",
        "cover_img_url",
        "vid_url",
    ]

    def clean_categories(self):
        if len(self.cleaned_data["categories"]) > 1:
            raise forms.ValidationError("Select no more than 1.")
        elif len(self.cleaned_data["categories"]) == 0:
            raise forms.ValidationError("Select at least one category")
        return self.cleaned_data["categories"]

    def clean_code(self):
        if not self.cleaned_data["code"].isalnum():
            raise forms.ValidationError("Only Alphanumeric string is allowed as Experience Code")
        return self.cleaned_data["code"]
