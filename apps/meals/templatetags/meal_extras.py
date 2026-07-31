from django import template

register = template.Library()


@register.filter
def meal_value(entry, meal_type):
    if not entry:
        return None
    return getattr(entry, meal_type)


@register.filter
def dict_get(d, key):
    if isinstance(d, dict):
        return d.get(key)
    return None
