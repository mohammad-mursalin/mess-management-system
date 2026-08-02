from decimal import Decimal

from django import template

register = template.Library()


@register.filter
def format_meal_value(value):
    if value is None:
        return '0'
    try:
        d = Decimal(str(value))
    except (TypeError, ValueError):
        return str(value)
    if d == d.to_integral_value():
        return str(int(d))
    return str(d)
