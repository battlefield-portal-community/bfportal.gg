import re
from urllib.parse import parse_qs, urlparse

from django.template.defaulttags import register


@register.filter
def get_item(dictionary, key):
    """Filter to get an item from a dictionary"""
    return dictionary.get(key)


@register.simple_tag
def get_social_account(user):
    """Tag that returns a social account for a django user"""
    usr = getattr(user, "socialaccount_set", None)
    if usr:
        all_acc = usr.all()
        if len(all_acc):
            return all_acc[0]
    else:
        return None


@register.filter(name="sub")
def subtract(value, arg):  # noqa: D103
    return value - arg


@register.simple_tag
def pagination_suffix(value):
    """Returns url for paginator suffix

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
    """Returns absolute value"""
    return abs(value)


@register.filter(name="expCode")
def get_exp_code(url: str) -> str:
    """Returns playgroundID from a portal URL

    playgroundId=45e436e0-4cf7-11ec-be7b-76c50778a53a
    """
    return parse_qs(urlparse(url).query).get("playgroundId", ["null"])[0]
