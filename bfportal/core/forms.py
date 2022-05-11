from django import forms
from urllib.parse import urlsplit, parse_qs
from core.models import ExperiencePage
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
        error_messages = {
            "categories": {
                "required": "Select at least one category"
            }
        }

    field_order = [
        "categories",
        "exp_url",
        "code",
        "title",
        "description",
        "tags",
        "no_players",
        "no_bots",
        "cover_img_url",
        "vid_url",
    ]



    def clean_categories(self):
        logger.debug("called")
        cats = self.cleaned_data["categories"]
        logger.debug(cats)
        if len(cats) > 1:
            raise forms.ValidationError("Select no more than 1.")
        return self.cleaned_data["categories"]

    def clean_code(self):
        code = self.cleaned_data["code"]
        if code and not code.isalnum():
            raise forms.ValidationError("can only contain alphanumeric characters")
        return self.cleaned_data["code"]

    def clean_exp_url(self):
        url = self.cleaned_data["exp_url"]
        if url:
            # SplitResult(
            #    scheme='https',
            #    netloc='portal.battlefield.com',
            #    path='/experience/package/era',
            #    params='',
            #    query='playgroundId=962f5460-8125-11ec-9c80-6204a0ec4852&test=true',
            #    fragment=''
            # )
            parsed_url = urlsplit(url)
            query_dict = parse_qs(parsed_url.query)
            if parsed_url.netloc != "portal.battlefield.com":
                logger.warning(f"Invalid url {url} submitted ")
                raise forms.ValidationError(
                    "only a URL from https://portal.battlefield.com/ is allowed",
                    code='invalid_domain'
                )
            elif "playgroundId" not in query_dict.keys():
                logger.info(f"url without playgroundId passed {url}")
                raise forms.ValidationError(
                    "must contain Playground ID",
                    code='no_playground_id'
                )
        return url

