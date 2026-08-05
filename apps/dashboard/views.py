from datetime import date, timedelta

from django.db.models import F, Sum
from django.shortcuts import render
from django.utils import timezone

from apps.cycles.models import Cycle
from apps.cycles.services import compute_cycle_due
from apps.groceries.models import GroceryBill, ExtraGrocery
from apps.bills.models import FixedBill
from apps.meals.selectors import get_daily_counts, member_guest_meals_for_cycle, member_own_meals_for_cycle
from apps.meals.models import MealEntry
from apps.members.models import Member, MemberCycle
from decimal import Decimal


def home(request):
    cycle = Cycle.objects.filter(status='open').first()
    today = timezone.now().date()

    today_counts = get_daily_counts(today)

    last_updated = None
    members = []
    today_meal_status = []

    if cycle:
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


def _get_selected_cycle(request, default_to_open=True):
    cycle_param = request.GET.get('cycle')
    if cycle_param == 'previous':
        closed = Cycle.objects.filter(status='closed').order_by('-start_date').first()
        if closed:
            return closed, 'previous'
        return Cycle.objects.filter(status='open').first(), 'current'
    elif cycle_param == 'current':
        return Cycle.objects.filter(status='open').first(), 'current'
    else:
        if default_to_open:
            return Cycle.objects.filter(status='open').first(), 'current'
        closed = Cycle.objects.filter(status='closed').order_by('-start_date').first()
        if closed:
            return closed, 'previous'
        return Cycle.objects.filter(status='open').first(), 'current'


def month_summary(request):
    cycle, cycle_mode = _get_selected_cycle(request, default_to_open=True)

    total_grocery = Decimal('0')
    total_extra_grocery = Decimal('0')
    total_fixed_bills = Decimal('0')
    member_due_rows = []
    is_estimated = False
    no_meals_logged = False
    total_expense_sum = Decimal('0')
    total_balance_negative = Decimal('0')
    total_balance_positive = Decimal('0')
    actual_meal_rate = Decimal('0')
    fixed_member_rate = Decimal('30')
    total_member_meals = Decimal('0')
    total_guest_meals = Decimal('0')
    total_meals = Decimal('0')

    has_previous = Cycle.objects.filter(status='closed').exists()

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

        if cycle.status == 'open':
            is_estimated = True
            computed = compute_cycle_due(cycle)
            actual_meal_rate = computed['actual_meal_rate']
            fixed_member_rate = computed['fixed_member_rate']
            total_member_meals = computed['total_member_meals']
            total_guest_meals = computed['total_guest_meals']
            total_meals = computed['total_meals']

            due_rows = computed['rows']
            no_meals_logged = total_meals == 0 and bool(due_rows)

            total_expense_sum = sum((row['total_expense'] for row in due_rows), Decimal('0'))
            total_balance_negative = sum(
                (abs(row['balance']) for row in due_rows if row['balance'] < 0),
                Decimal('0'),
            )
            total_balance_positive = sum(
                (row['balance'] for row in due_rows if row['balance'] > 0),
                Decimal('0'),
            )

            for row in due_rows:
                member_due_rows.append({
                    'name': row['member_cycle'].member.name,
                    'own_meals': row['own_meals'],
                    'guest_meals': row['guest_meals'],
                    'meal_expense': row['meal_expense'],
                    'extra_bill_share': row['total_expense'] - row['meal_expense'],
                    'total_expense': row['total_expense'],
                    'deposit': row['deposit'],
                    'balance': row['balance'],
                })
        else:
            member_cycles = cycle.member_cycles.select_related('member').all()
            for mc in member_cycles:
                total_expense = mc.computed_due if mc.computed_due is not None else Decimal('0')
                balance = mc.deposit_amount - total_expense
                own_meals = member_own_meals_for_cycle(mc)
                guest_meals = member_guest_meals_for_cycle(mc)
                member_due_rows.append({
                    'name': mc.member.name,
                    'own_meals': own_meals,
                    'guest_meals': guest_meals,
                    'meal_expense': None,
                    'extra_bill_share': None,
                    'total_expense': total_expense,
                    'deposit': mc.deposit_amount,
                    'balance': balance,
                })
                total_expense_sum += total_expense
                if balance < 0:
                    total_balance_negative += abs(balance)
                elif balance > 0:
                    total_balance_positive += balance

    return render(request, 'dashboard/month_summary.html', {
        'current_cycle': cycle,
        'cycle_mode': cycle_mode,
        'has_previous': has_previous,
        'total_grocery': total_grocery,
        'total_extra_grocery': total_extra_grocery,
        'total_fixed_bills': total_fixed_bills,
        'member_due_rows': member_due_rows,
        'is_estimated': is_estimated,
        'no_meals_logged': no_meals_logged,
        'total_expense_sum': total_expense_sum,
        'total_balance_negative': total_balance_negative,
        'total_balance_positive': total_balance_positive,
        'actual_meal_rate': actual_meal_rate,
        'fixed_member_rate': fixed_member_rate,
        'total_member_meals': total_member_meals,
        'total_guest_meals': total_guest_meals,
        'total_meals': total_meals,
    })


def meal_history(request):
    cycle, cycle_mode = _get_selected_cycle(request, default_to_open=True)
    selected_member_id = request.GET.get('member')

    member_qs = Member.objects.filter(is_active=True).order_by('name')
    all_members = list(member_qs)

    selected_member = None
    entries = []

    if cycle:
        start = cycle.start_date
        end = cycle.end_date or timezone.now().date()

        if selected_member_id:
            try:
                selected_member = Member.objects.get(pk=selected_member_id)
                mc = MemberCycle.objects.filter(
                    member=selected_member, cycle=cycle
                ).first()
                if mc:
                    entry_map = {}
                    for entry in mc.meal_entries.filter(
                        entry_date__gte=start,
                        entry_date__lte=end,
                    ):
                        entry_map[entry.entry_date] = entry

                    current = start
                    while current <= end:
                        if current in entry_map:
                            entries.append({
                                'date': current,
                                'entry': entry_map[current],
                            })
                        else:
                            entries.append({
                                'date': current,
                                'entry': None,
                            })
                        current += timedelta(days=1)
            except Member.DoesNotExist:
                pass

    has_previous = Cycle.objects.filter(status='closed').exists()

    return render(request, 'dashboard/meal_history.html', {
        'current_cycle': cycle,
        'cycle_mode': cycle_mode,
        'has_previous': has_previous,
        'all_members': all_members,
        'selected_member': selected_member,
        'entries': entries,
    })
