import re
from urllib.parse import parse_qs, urlparse

from core.helper import markdownify
from core.models import ExperiencePage, HomePage, SubCategory
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.template.defaulttags import register
from django.templatetags.static import static


@register.filter
def show_markdown(text):
    """Returns HTML from Markdown text"""
    return markdownify(text)


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


@register.filter("hasCategory")
def check_cats(cats: SubCategory, cat: str):
    """Returns True if a category is in queryset"""
    return cat in list(map(lambda x: x.name, cats.all()))


@register.filter("is_liked_by_user")
def check_liked(post: ExperiencePage, request: HttpRequest) -> bool:
    """Returns True if liked by user"""
    if request.user.is_authenticated:
        return post in request.user.profile.liked.all()


@register.filter("check_permission")
def check_permission(user, permission):
    """Returns True if user has the 'permission'"""
    return user.has_perm(permission)


@register.filter("check_group")
def check_group(user: User, group):
    """Returns True if user has the 'permission'"""
    return user.groups.filter(name__iexact=group)


@register.filter
def classname(obj):
    """Returns obj type"""
    return type(obj)


@register.filter
def replace(value, arg):
    """
    Replacing filter

    Use `{{ "aaa"|replace:"a|b" }}`
    """
    if len(arg.split("|")) != 2:
        return value

    what, to = arg.split("|")
    return value.replace(what, to)


@register.filter
def get_opg_image_url(
    request: HttpRequest, page: ExperiencePage | HomePage | None = None
) -> str:
    """Returns image url for ogp meta tag"""
    url_prefix = f"{request.scheme}://{request.META.get('HTTP_HOST', '')}"
    if page:
        if isinstance(page, ExperiencePage) and page.cover_img_url:
            return page.cover_img_url

    if result := static("images/default_meta.png"):
        return url_prefix + result

    return ""
