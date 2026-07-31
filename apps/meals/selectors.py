from django.db.models import Sum
from .models import MealEntry


def get_daily_counts(entry_date):
    entries = MealEntry.objects.filter(entry_date=entry_date)
    agg = entries.aggregate(
        breakfast_sum=Sum('breakfast'),
        lunch_sum=Sum('lunch'),
        dinner_sum=Sum('dinner'),
    )
    breakfast_raw = agg['breakfast_sum'] or 0
    return {
        'breakfast_count': int(breakfast_raw * 2),
        'lunch_count': int(agg['lunch_sum'] or 0),
        'dinner_count': int(agg['dinner_sum'] or 0),
    }
