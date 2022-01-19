from django import forms
from core.models import ExperiencePage, ExperiencesCategory


class ExperiencePageForm(forms.ModelForm):
    class Meta:
        model = ExperiencePage
        fields = [
            'title',
            'description',
            'categories',
            'exp_url',
            'code',
            'tags',
            'no_players',
            'no_bots',
            'cover_img_url',
            'vid_url'
        ]
