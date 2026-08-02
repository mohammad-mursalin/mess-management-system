from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum
from django.shortcuts import render
from django.utils import timezone

from cycles.models import Cycle
from groceries.models import GroceryBill, ExtraGrocery
from bills.models import FixedBill
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

        today_meal_status = []

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

            today_entry = mc.meal_entries.filter(entry_date=today).first()
            bf_val = today_entry.breakfast if today_entry else Decimal('0')
            ln_val = today_entry.lunch if today_entry else Decimal('0')
            dn_val = today_entry.dinner if today_entry else Decimal('0')
            today_meal_status.append({
                'name': mc.member.name,
                'breakfast': bf_val,
                'lunch': ln_val,
                'dinner': dn_val,
            })

    return render(request, 'dashboard/home.html', {
        'current_cycle': cycle,
        'today_counts': today_counts,
        'today': today,
        'last_updated': last_updated,
        'members': members,
        'today_meal_status': today_meal_status,
    })


@login_required
def month_summary(request):
    cycle = Cycle.objects.filter(status='open').first()

    total_grocery = Decimal('0')
    total_extra_grocery = Decimal('0')
    total_fixed_bills = Decimal('0')
    total_meals = 0.0
    member_meals = []

    if cycle:
        grocery_agg = GroceryBill.objects.filter(cycle=cycle).aggregate(
            total=Sum('total_amount')
        )
        total_grocery = grocery_agg['total'] or Decimal('0')

        extra_agg = ExtraGrocery.objects.filter(cycle=cycle).aggregate(
            total=Sum(F('quantity') * F('price'))
        )
        total_extra_grocery = extra_agg['total'] or Decimal('0')

        fixed_agg = FixedBill.objects.filter(cycle=cycle).aggregate(
            total=Sum('amount')
        )
        total_fixed_bills = fixed_agg['total'] or Decimal('0')

        end_date = cycle.end_date or timezone.now().date()

        for mc in cycle.member_cycles.select_related('member'):
            meals = mc.meal_entries.filter(
                entry_date__gte=cycle.start_date,
                entry_date__lte=end_date,
            )
            agg = meals.aggregate(
                bf=Sum('breakfast'),
                ln=Sum('lunch'),
                dn=Sum('dinner'),
            )
            bf = float(agg['bf'] or 0)
            ln = int(agg['ln'] or 0)
            dn = int(agg['dn'] or 0)
            member_meals.append({
                'name': mc.member.name,
                'breakfast': bf,
                'lunch': ln,
                'dinner': dn,
                'total': round(bf + ln + dn, 1),
            })
            total_meals += round(bf + ln + dn, 1)

    return render(request, 'dashboard/month_summary.html', {
        'current_cycle': cycle,
        'total_grocery': total_grocery,
        'total_extra_grocery': total_extra_grocery,
        'total_fixed_bills': total_fixed_bills,
        'total_meals': total_meals,
        'member_meals': member_meals,
    })
