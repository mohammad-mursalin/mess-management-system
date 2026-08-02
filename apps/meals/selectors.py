from decimal import Decimal

from django.db.models import Sum
from .models import MealEntry


MEAL_BASE_UNITS = {
    'breakfast': Decimal('0.5'),
    'lunch': Decimal('1'),
    'dinner': Decimal('1'),
}


def member_units(value, meal_type):
    if value is None or value <= 0:
        return Decimal('0')
    return MEAL_BASE_UNITS.get(meal_type, Decimal('0'))


def guest_units(value, meal_type):
    if value is None or value <= 0:
        return Decimal('0')
    base = MEAL_BASE_UNITS.get(meal_type, Decimal('0'))
    return max(Decimal('0'), value - base)


def get_daily_counts(entry_date):
    entries = MealEntry.objects.filter(entry_date=entry_date)
    agg = entries.aggregate(
        breakfast_sum=Sum('breakfast'),
        lunch_sum=Sum('lunch'),
        dinner_sum=Sum('dinner'),
    )
    breakfast_raw = agg['breakfast_sum'] or Decimal('0')
    lunch_raw = agg['lunch_sum'] or Decimal('0')
    dinner_raw = agg['dinner_sum'] or Decimal('0')
    return {
        'breakfast_count': int(breakfast_raw * 2),
        'lunch_count': int(lunch_raw),
        'dinner_count': int(dinner_raw),
    }
