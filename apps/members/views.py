from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from apps.cycles.models import Cycle
from .forms import AddMemberForm, EditMemberForm
from .models import Member, MemberCycle


def get_current_cycle():
    return Cycle.objects.filter(status='open').first()


def _build_member_data(cycle):
    """Build list of member dicts with current cycle info."""
    members = Member.objects.all().order_by('name')
    result = []

    if cycle:
        member_cycles = {
            mc.member_id: mc for mc in
            cycle.member_cycles.select_related('member').all()
        }
        for member in members:
            mc = member_cycles.get(member.id)
            result.append({
                'member': member,
                'join_date': mc.join_date if mc else None,
                'leave_date': mc.leave_date if mc else None,
                'deposit': mc.deposit_amount if mc else None,
            })
    else:
        for member in members:
            result.append({
                'member': member,
                'join_date': None,
                'leave_date': None,
                'deposit': None,
            })

    return members, result


def _render_page(request, cycle, add_form=None, editing_member=None,
                 edit_form=None, show_add_modal=False):
    """Render the member list page with optional modal/form state."""
    _, member_data = _build_member_data(cycle)

    if add_form is None:
        add_form = AddMemberForm(initial_join_date=cycle.start_date if cycle else None)

    ctx = {
        'current_cycle': cycle,
        'has_cycle': cycle is not None,
        'members': member_data,
        'add_form': add_form,
        'show_add_modal': show_add_modal,
    }

    if editing_member:
        ctx['editing_member'] = editing_member
        ctx['edit_form'] = edit_form or EditMemberForm()

    return render(request, 'members/member_list.html', ctx)


@login_required
def member_list(request):
    cycle = get_current_cycle()
    return _render_page(request, cycle)


@login_required
def add_member(request):
    cycle = get_current_cycle()

    if not cycle:
        messages.error(request, "Open a cycle before adding members.")
        return redirect('member_list')

    if request.method == 'POST':
        form = AddMemberForm(request.POST, initial_join_date=cycle.start_date)
        if form.is_valid():
            with transaction.atomic():
                member = Member.objects.create(
                    name=form.cleaned_data['name'],
                    is_active=True,
                )
                join_date = form.cleaned_data.get('join_date') or cycle.start_date
                MemberCycle.objects.create(
                    member=member,
                    cycle=cycle,
                    join_date=join_date,
                    deposit_amount=form.cleaned_data.get('deposit_amount') or 0,
                )
            messages.success(request, f"Member '{member.name}' added.")
            return redirect('member_list')
        return _render_page(request, cycle, add_form=form, show_add_modal=True)

    return redirect('member_list')


@login_required
def edit_member(request, member_id):
    cycle = get_current_cycle()

    if not cycle:
        messages.error(request, "No open cycle found.")
        return redirect('member_list')

    member = get_object_or_404(Member, pk=member_id)
    mc, _ = MemberCycle.objects.get_or_create(
        member=member, cycle=cycle,
        defaults={'join_date': cycle.start_date, 'deposit_amount': 0},
    )

    if request.method == 'POST':
        form = EditMemberForm(request.POST)
        if form.is_valid():
            member.name = form.cleaned_data['name']
            member.save()
            mc.join_date = form.cleaned_data['join_date']
            mc.deposit_amount = form.cleaned_data.get('deposit_amount') or 0
            mc.save()
            messages.success(request, f"Member '{member.name}' updated.")
            return redirect('member_list')
        return _render_page(request, cycle, editing_member=member, edit_form=form)

    form = EditMemberForm(initial={
        'name': member.name,
        'join_date': mc.join_date or cycle.start_date,
        'deposit_amount': mc.deposit_amount,
    })
    return _render_page(request, cycle, editing_member=member, edit_form=form)


@login_required
@require_POST
def toggle_member_active(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    cycle = get_current_cycle()

    if member.is_active:
        member.is_active = False
        if cycle:
            MemberCycle.objects.filter(member=member, cycle=cycle).update(leave_date=date.today())
        messages.success(request, f"Member '{member.name}' deactivated.")
    else:
        member.is_active = True
        if cycle:
            MemberCycle.objects.filter(member=member, cycle=cycle).update(leave_date=None)
        messages.success(request, f"Member '{member.name}' reactivated.")

    member.save()
    return redirect('member_list')
