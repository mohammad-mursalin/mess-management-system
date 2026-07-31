from django.db import transaction
from django.utils import timezone
from .models import Cycle
from members.models import Member, MemberCycle


@transaction.atomic
def close_month(cycle):
    cycle.status = 'closed'
    cycle.end_date = timezone.now().date()
    cycle.save()
    for mc in cycle.member_cycles.select_related('member').all():
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
