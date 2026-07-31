from django.shortcuts import render
from django.utils import timezone
from django.db.models import Sum

from cycles.models import Cycle
from meals.selectors import get_daily_counts


def home(request):
    cycle = Cycle.objects.filter(status='open').first()
    today = timezone.now().date()

    today_counts = get_daily_counts(today)

    last_updated = None
    members = []

    if cycle:
        from meals.models import MealEntry
        last_updated = (
            MealEntry.objects
            .filter(member_cycle__cycle=cycle, entry_date=today)
            .order_by('-updated_at')
            .values_list('updated_at', flat=True)
            .first()
        )

        start_date = cycle.start_date
        end_date = today if cycle.status == 'open' else (cycle.end_date or today)

        member_cycles = cycle.member_cycles.select_related('member')

        for mc in member_cycles:
            meals = mc.meal_entries.filter(
                entry_date__gte=start_date,
                entry_date__lte=end_date,
            )
            agg = meals.aggregate(
                bf=Sum('breakfast'),
                ln=Sum('lunch'),
                dn=Sum('dinner'),
            )
            members.append({
                'name': mc.member.name,
                'deposit': mc.deposit_amount,
                'breakfast': float(agg['bf'] or 0),
                'lunch': int(agg['ln'] or 0),
                'dinner': int(agg['dn'] or 0),
            })

    return render(request, 'dashboard/home.html', {
        'current_cycle': cycle,
        'today_counts': today_counts,
        'today': today,
        'last_updated': last_updated,
        'members': members,
    })
