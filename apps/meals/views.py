from datetime import timedelta, datetime

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Q
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.utils import timezone

from cycles.models import Cycle
from members.models import MemberCycle
from meals.models import MealEntry
from meals.selectors import get_daily_counts


def logout_view(request):
    logout(request)
    return redirect('/accounts/login/')


@login_required
def entry_grid(request):
    cycle = Cycle.objects.filter(status='open').first()
    today = timezone.now().date()

    no_open_cycle = cycle is None

    date_str = request.GET.get('date')
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = today
    else:
        selected_date = today

    prev_date = selected_date - timedelta(days=1)
    next_date = selected_date + timedelta(days=1)

    counts = get_daily_counts(selected_date)

    member_cycles = []
    entry_map = {}

    if cycle:
        member_cycles = MemberCycle.objects.filter(
            cycle=cycle,
            join_date__lte=selected_date,
        ).filter(
            Q(leave_date__isnull=True) | Q(leave_date__gte=selected_date)
        ).select_related('member')

        for mc in member_cycles:
            entry = MealEntry.objects.filter(
                member_cycle=mc,
                entry_date=selected_date,
            ).first()
            entry_map[mc.id] = entry

    return render(request, 'meals/entry_grid.html', {
        'open_cycle': cycle,
        'no_open_cycle': no_open_cycle,
        'member_cycles': member_cycles,
        'entry_map': entry_map,
        'selected_date': selected_date,
        'prev_date': prev_date,
        'next_date': next_date,
        'counts': counts,
        'BREAKFAST_CHOICES': MealEntry.BREAKFAST_CHOICES,
        'LUNCH_CHOICES': MealEntry.LUNCH_CHOICES,
        'DINNER_CHOICES': MealEntry.DINNER_CHOICES,
    })


@login_required
def meal_cell_update(request):
    if request.method != 'POST':
        return HttpResponse('')

    member_cycle_id = request.POST.get('member_cycle_id')
    entry_date_str = request.POST.get('entry_date')
    meal_type = request.POST.get('meal_type')
    value = request.POST.get('value')

    if not member_cycle_id or not entry_date_str or not meal_type:
        return HttpResponseBadRequest('Missing parameters')

    try:
        mc = MemberCycle.objects.get(pk=member_cycle_id)
    except MemberCycle.DoesNotExist:
        return HttpResponse('')

    try:
        entry_date = datetime.strptime(entry_date_str, '%Y-%m-%d').date()
    except ValueError:
        return HttpResponseBadRequest('Invalid date')

    valid_values = {
        'breakfast': [0, 0.5, 1],
        'lunch': [0, 1],
        'dinner': [0, 1],
    }

    if meal_type not in valid_values:
        return HttpResponseBadRequest('Invalid meal type')

    try:
        value = float(value)
    except (TypeError, ValueError):
        value = 0

    cell_error = None
    entry = None

    try:
        entry, created = MealEntry.objects.get_or_create(
            member_cycle=mc,
            entry_date=entry_date,
            defaults={'member_cycle': mc, 'entry_date': entry_date, 'updated_by': request.user},
        )

        if value not in valid_values[meal_type]:
            cell_error = 'Invalid meal value.'
        elif (mc.join_date and entry_date < mc.join_date) or \
             (mc.leave_date and entry_date > mc.leave_date):
            cell_error = 'Outside member join/leave window.'
        else:
            setattr(entry, meal_type, value)
            entry.updated_by = request.user
            entry.save()
    except (IntegrityError, ValidationError, ValueError) as e:
        if hasattr(e, 'messages') and e.messages:
            cell_error = e.messages[0]
        else:
            cell_error = str(e)

    meal_choices_map = {
        'breakfast': MealEntry.BREAKFAST_CHOICES,
        'lunch': MealEntry.LUNCH_CHOICES,
        'dinner': MealEntry.DINNER_CHOICES,
    }

    return render(request, 'meals/partials/meal_cell.html', {
        'mc': mc,
        'entry': entry,
        'entry_date': entry_date,
        'meal_type': meal_type,
        'meal_choices': meal_choices_map[meal_type],
        'cell_error': cell_error,
    })
