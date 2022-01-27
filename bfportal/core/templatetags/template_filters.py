from django.template.defaulttags import register
from loguru import logger


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.simple_tag
def get_social_account(user):
    usr = getattr(user, 'socialaccount_set', None)
    if usr:
        all_acc = usr.all()
        if len(all_acc):
            return all_acc[0]
    else:
        return None
