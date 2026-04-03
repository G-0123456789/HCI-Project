from django import template

register = template.Library()


@register.filter
def dict_get(d, key):
    """{{ my_dict|dict_get:key }} — safely get a dict value by key."""
    if isinstance(d, dict):
        return d.get(key, '')
    return ''
