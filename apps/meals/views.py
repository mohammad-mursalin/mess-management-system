from django.shortcuts import redirect, render
from django.contrib.auth import logout
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from cycles.models import Cycle
from members.models import MemberCycle
from meals.models import MealEntry


def logout_view(request):
    logout(request)
    return redirect('/accounts/login/')


@login_required
def entry_grid(request):
    cycle = Cycle.objects.filter(status='open').first()
    today = timezone.now().date()

    member_cycles = []
    if cycle:
        member_cycles = MemberCycle.objects.filter(cycle=cycle).select_related('member')

    members = []
    for mc in member_cycles:
        entry, created = MealEntry.objects.get_or_create(
            member_cycle=mc,
            entry_date=today,
            defaults={'member_cycle': mc, 'entry_date': today},
        )
        members.append({
            'member_cycle': mc,
            'entry': entry,
        })

    return render(request, 'meals/entry_grid.html', {
        'cycle': cycle,
        'today': today,
        'members': members,
    })


@login_required
def meal_cell_update(request):
    if request.method != 'POST':
        return HttpResponse('')

    entry_id = request.POST.get('entry_id')
    meal_type = request.POST.get('meal_type')
    value = request.POST.get('value')

    try:
        entry = MealEntry.objects.get(pk=entry_id)
    except MealEntry.DoesNotExist:
        return HttpResponse('')

    valid_values = {
        'breakfast': [0, 0.5, 1],
        'lunch': [0, 1],
        'dinner': [0, 1],
    }

    try:
        value = float(value)
    except (TypeError, ValueError):
        value = 0

    if meal_type in valid_values and value in valid_values[meal_type]:
        setattr(entry, meal_type, value)
        entry.save()

    return render(request, 'meals/partials/meal_cell.html', {
        'entry': entry,
        'meal_type': meal_type,
    })
