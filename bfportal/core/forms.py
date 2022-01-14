from django import forms
from core.models import ExperiencePage

class ExperiencePageForm(forms.ModelForm):
    class Meta:
        model = ExperiencePage
        fields = [
            'name',
            'description',
            'exp_url',
            'code',
            'no_players',
            'no_bots',
            'cover_img_url',
            'vid_url'
        ]