from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from django.db.models import F, Sum
from django.utils import timezone

from apps.meals.selectors import (
    member_guest_meals_for_cycle,
    member_own_meals_for_cycle,
    total_guest_meals_for_cycle,
    total_member_meals_for_cycle,
)
from apps.groceries.models import GroceryBill, ExtraGrocery
from apps.bills.models import FixedBill
from .models import Cycle
from apps.members.models import MemberCycle


def compute_cycle_due(cycle):
    total_grocery_bill = sum(
        (bill.total_amount or Decimal('0')) for bill in GroceryBill.objects.filter(cycle=cycle)
    )
    extra_grocery_agg = ExtraGrocery.objects.filter(cycle=cycle).aggregate(
        total=Sum(F('quantity') * F('price'))
    )
    total_grocery_bill += extra_grocery_agg['total'] or Decimal('0')

    total_fixed_bills = FixedBill.objects.filter(cycle=cycle).aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0')

    total_member_meals = total_member_meals_for_cycle(cycle)
    total_guest_meals = total_guest_meals_for_cycle(cycle)
    total_meals = total_member_meals + total_guest_meals

    member_cycles = cycle.member_cycles.select_related('member').all()
    active_member_count = member_cycles.count()

    if total_meals == 0:
        actual_meal_rate = Decimal('0')
    else:
        actual_meal_rate = total_grocery_bill / total_meals

    if active_member_count == 0:
        extra_bill_per_member = Decimal('0')
    else:
        total_extra_bill = (
            total_grocery_bill
            - (total_guest_meals * actual_meal_rate)
            - (total_member_meals * cycle.fixed_member_rate)
            + total_fixed_bills
        )
        extra_bill_per_member = total_extra_bill / active_member_count

    results = []
    for mc in member_cycles:
        own = member_own_meals_for_cycle(mc)
        guest = member_guest_meals_for_cycle(mc)

        meal_expense = (
            own * cycle.fixed_member_rate
        ) + (
            guest * actual_meal_rate
        )
        total_expense = meal_expense + extra_bill_per_member
        balance = mc.deposit_amount - total_expense

        results.append({
            'member_cycle': mc,
            'own_meals': own,
            'guest_meals': guest,
            'meal_expense': meal_expense,
            'total_expense': total_expense,
            'deposit': mc.deposit_amount,
            'balance': balance,
        })

    return {
        'rows': results,
        'actual_meal_rate': actual_meal_rate,
        'fixed_member_rate': cycle.fixed_member_rate,
        'total_member_meals': total_member_meals,
        'total_guest_meals': total_guest_meals,
        'total_meals': total_meals,
        'total_grocery_bill': total_grocery_bill,
        'total_fixed_bills': total_fixed_bills,
        'total_extra_bill': total_extra_bill if active_member_count > 0 else Decimal('0'),
        'extra_bill_per_member': extra_bill_per_member,
    }


@transaction.atomic
def close_month(cycle):
    cycle.status = 'closed'
    cycle.end_date = timezone.now().date()
    cycle.save()

    computed = compute_cycle_due(cycle)
    for item in computed['rows']:
        mc = item['member_cycle']
        mc.computed_due = item['total_expense']
        mc.settled = True
        mc.save()


@transaction.atomic
def open_new_cycle(label=None, start_date=None):
    open_cycle = Cycle.objects.filter(status='open').first()
    if open_cycle:
        raise ValueError("Close the current cycle before starting a new one.")

    if start_date is None:
        start_date = timezone.now().date()

    if label is None:
        label = start_date.strftime('%Y-%m')

    cycle = Cycle.objects.create(
        label=label,
        start_date=start_date,
        status='open',
    )

    active_members = Member.objects.filter(is_active=True)
    member_cycles = [
        MemberCycle(
            member=member,
            cycle=cycle,
            join_date=start_date,
            deposit_amount=0,
        )
        for member in active_members
    ]
    MemberCycle.objects.bulk_create(member_cycles)

    return cycle


def update_fixed_member_rate(cycle, rate):
    cycle.fixed_member_rate = rate
    cycle.save()
