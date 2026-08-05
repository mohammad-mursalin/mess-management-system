from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from apps.cycles.models import Cycle
from .models import FixedBill
from .forms import FixedBillForm


def open_cycle():
    return Cycle.objects.filter(status='open').first()


def _selected_cycle(request):
    mode = request.GET.get('cycle')
    if mode == 'previous':
        closed = Cycle.objects.filter(status='closed').order_by('-start_date').first()
        if closed:
            return closed, 'previous'
    return Cycle.objects.filter(status='open').first(), 'current'


def _has_previous():
    return Cycle.objects.filter(status='closed').exists()


def _bills_for(cycle):
    if not cycle:
        return FixedBill.objects.none()
    return (
        FixedBill.objects
        .select_related('cycle')
        .filter(cycle=cycle)
        .order_by('-bill_date', '-id')
    )


def _ctx(cycle, bills, form, editing_bill, editing, cycle_mode='current', is_current=True):
    return {
        'current_cycle': cycle,
        'has_cycle': cycle is not None,
        'bills': bills,
        'bill_form': form,
        'editing_bill': editing_bill,
        'is_editing': editing,
        'cycle_mode': cycle_mode,
        'has_previous': _has_previous(),
        'is_current_cycle': is_current,
    }


@login_required
def bill_list(request):
    c, cycle_mode = _selected_cycle(request)
    bills = _bills_for(c)
    is_current = c and c.status == 'open'
    form = FixedBillForm(cycle=c) if is_current else None
    return render(request, 'bills/bill_list.html', _ctx(c, bills, form, None, False, cycle_mode, is_current))


@login_required
def bill_add(request):
    c = open_cycle()
    if not c:
        messages.error(
            request,
            "Open a cycle in the Cycles admin before logging fixed bills.",
        )
        return redirect('fixed_bill_list')
    form = FixedBillForm(request.POST, cycle=c)
    if form.is_valid():
        bill = form.save(commit=False)
        bill.cycle = c
        bill.save()
        messages.success(
            request,
            f"Fixed bill ({bill.get_bill_type_display()}) of ৳{bill.amount} saved.",
        )
        return redirect('fixed_bill_list')
    return render(
        request, 'bills/bill_list.html', _ctx(c, _bills_for(c), form, None, False, 'current', True)
    )


@login_required
def bill_edit(request, bill_id):
    bill = get_object_or_404(FixedBill, pk=bill_id)
    c = bill.cycle
    form = FixedBillForm(request.POST or None, instance=bill, cycle=c)
    return render(
        request, 'bills/bill_list.html', _ctx(c, _bills_for(c), form, bill, True, 'current', True)
    )


@login_required
def bill_update(request, bill_id):
    bill = get_object_or_404(FixedBill, pk=bill_id)
    c = bill.cycle
    form = FixedBillForm(request.POST, instance=bill, cycle=c)
    if form.is_valid():
        form.save()
        messages.success(request, "Fixed bill updated.")
        return redirect('fixed_bill_list')
    return render(
        request, 'bills/bill_list.html', _ctx(c, _bills_for(c), form, bill, True, 'current', True)
    )


@login_required
def bill_delete(request, bill_id):
    bill = get_object_or_404(FixedBill, pk=bill_id)
    if request.method == 'POST':
        label = bill.get_bill_type_display()
        amount = bill.amount
        bill.delete()
        messages.success(request, f"Deleted {label} bill of ৳{amount}.")
    return redirect('fixed_bill_list')
