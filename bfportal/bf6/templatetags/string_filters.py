from django.template.defaulttags import register


@register.filter(name="startswith")
def startswith(text, starts):
    """Return True if ``text`` is a string that starts with ``starts``."""
    if isinstance(text, str):
        return text.startswith(starts)
    return False
