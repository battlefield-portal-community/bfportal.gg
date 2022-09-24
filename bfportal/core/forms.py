from urllib.parse import parse_qs, urlsplit

import requests
from ajax_select.fields import AutoCompleteSelectMultipleField
from core.models import ExperiencePage, ExperiencesCategory, SubCategory
from django import forms
from loguru import logger


class ExperiencePageForm(forms.ModelForm):
    """ModelForm for making an input form to submit a new experience"""

    def __init__(self, *args, **kwargs):
        super(ExperiencePageForm, self).__init__(*args, **kwargs)
        self.ignore = ["sub_categories", "allow_editing"]
        self.fields["category"].queryset = ExperiencesCategory.objects.filter(
            selectable_on_form=True
        )
        self.fields["sub_categories"].queryset = SubCategory.objects.filter(
            selectable_on_form=True
        )

    creators = AutoCompleteSelectMultipleField(
        "DiscordUsers",
        required=False,
        help_text="Add additional creators",
        widget_options={"attrs": {"required": False}},
        plugin_options={"position": {"my": "left top+10", "at": "left bottom"}},
    )
    tags = AutoCompleteSelectMultipleField(
        "tags",
        required=False,
        help_text="Add tags to your experience",
        widget_options={"attrs": {"required": False}},
        plugin_options={"position": {"my": "left top+10", "at": "left bottom"}},
    )

    class Meta:
        model = ExperiencePage
        exclude = ["featured"]
        fields = [
            "title",
            "description",
            "category",
            "sub_categories",
            "exp_url",
            "code",
            "no_players",
            "no_bots",
            "cover_img_url",
            "vid_url",
            "creators",
            "tags",
            "allow_editing",
        ]
        error_messages = {"category": {"required": "Select at least one category"}}

    field_order = [
        "category",
        "exp_url",
        "code",
        "title",
        "description",
        "creators",
        "tags",
        "no_players",
        "no_bots",
        "sub_categories",
        "cover_img_url",
        "vid_url",
    ]

    def clean_code(self):
        """Called when code field is being validated"""
        code = self.cleaned_data["code"]
        if code and not code.isalnum():
            raise forms.ValidationError("can only contain alphanumeric characters")
        return self.cleaned_data["code"]

    def clean_exp_url(self):
        """Called when experience url field is being validated"""
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
                    code="invalid_domain",
                )
            elif "playgroundId" not in query_dict.keys():
                logger.info(f"url without playgroundId passed {url}")
                raise forms.ValidationError(
                    "must contain Playground ID", code="no_playground_id"
                )
        return url

    def clean_cover_img_url(self):
        """Raises ValidationError if image link does not return content-type: 'image/*' like header"""
        header_resp = requests.head(
            self.cleaned_data["cover_img_url"], allow_redirects=True
        )
        if not header_resp.headers["content-type"].startswith("image"):
            raise forms.ValidationError(
                "Image url is invalid, make sure it is a direct link to the image"
            )
        return self.cleaned_data["cover_img_url"]
