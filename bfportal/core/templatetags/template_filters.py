import re
from urllib.parse import parse_qs, urlparse

from django.template.defaulttags import register


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.simple_tag
def get_social_account(user):
    usr = getattr(user, "socialaccount_set", None)
    if usr:
        all_acc = usr.all()
        if len(all_acc):
            return all_acc[0]
    else:
        return None


@register.filter(name="sub")
def subtract(value, arg):
    return value - arg


@register.simple_tag
def pagination_suffix(value):
    """
    returns url for paginator suffix
    """
    """
        sample
            [Input] : tag=management&tag=since&page=3
            [Output] : &tag=management&tag=since
    """
    suffix_params = re.sub(r"[&?]?page=\d+", "", value)
    if len(suffix_params):
        return ("&" + suffix_params).replace("&&", "&")
    else:
        return ""


@register.filter(name="abs")
def abs_filter(value):
    return abs(value)


@register.filter(name="expCode")
def get_exp_code(url: str) -> str:
    #  playgroundId=45e436e0-4cf7-11ec-be7b-76c50778a53a
    return parse_qs(urlparse(url).query).get("playgroundId", ["null"])[0]
