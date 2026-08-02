from decimal import Decimal

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


@register.filter
def meal_guest_count(value, meal_type):
    try:
        v = Decimal(str(value))
    except (TypeError, ValueError):
        return 0
    if v is None or v <= 0:
        return 0
    base = Decimal('0.5') if meal_type == 'breakfast' else Decimal('1')
    guest = max(Decimal('0'), v - base)
    step = Decimal('0.5') if meal_type == 'breakfast' else Decimal('1')
    if step <= 0:
        return 0
    return int(guest / step)


@register.simple_tag
def stepper_values(current_val, step):
    try:
        v = Decimal(str(current_val))
        s = Decimal(str(step))
        minus = max(Decimal('0'), v - s)
        plus = v + s
        return {'minus': minus, 'plus': plus}
    except (TypeError, ValueError):
        return {'minus': current_val, 'plus': current_val}
