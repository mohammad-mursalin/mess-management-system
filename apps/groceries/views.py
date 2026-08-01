
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from cycles.models import Cycle
from .models import GroceryBill, ExtraGrocery
from .forms import GroceryBillForm, ExtraGroceryForm
from .utils import sync_bill_items, member_choices_json


def open_cycle():
    return Cycle.objects.filter(status='open').first()


@login_required
def bill_list(request):
    c = open_cycle()
    bills = _bills_for(c)
    form = GroceryBillForm(cycle=c) if c else GroceryBillForm()
    return render(request, 'groceries/bill_list.html', _ctx(c, bills, form, None, False))


@login_required
def bill_add(request):
    c = open_cycle()
    if not c:
        messages.error(request, "Open a cycle in Cycles admin before logging bills.")
        return redirect('bill_list')
    form = GroceryBillForm(request.POST, cycle=c)
    if form.is_valid():
        bill = form.save(commit=False)
        bill.cycle = c
        bill.save()
        sync_bill_items(bill, request.POST)
        _mismatch_note(request, bill)
        messages.success(request, f"Grocery bill of \u20b9{bill.total_amount} saved.")
        return redirect('bill_list')
    return render(request, 'groceries/bill_list.html', _ctx(c, _bills_for(c), form, None, False))


@login_required
def bill_edit(request, bill_id):
    bill = get_object_or_404(GroceryBill, pk=bill_id)
    c = bill.cycle
    form = GroceryBillForm(request.POST or None, instance=bill, cycle=c)
    return render(request, 'groceries/bill_list.html', _ctx(c, _bills_for(c), form, bill, True))


@login_required
def bill_update(request, bill_id):
    bill = get_object_or_404(GroceryBill, pk=bill_id)
    c = bill.cycle
    form = GroceryBillForm(request.POST, instance=bill, cycle=c)
    if form.is_valid():
        bill = form.save(commit=False)
        bill.cycle = c
        bill.save()
        sync_bill_items(bill, request.POST)
        _mismatch_note(request, bill)
        messages.success(request, "Grocery bill updated.")
        return redirect('bill_list')
    return render(request, 'groceries/bill_list.html', _ctx(c, _bills_for(c), form, bill, True))


@login_required
def bill_delete(request, bill_id):
    bill = get_object_or_404(GroceryBill, pk=bill_id)
    if request.method == 'POST':
        amount = bill.total_amount
        bill.delete()
        messages.success(request, f"Deleted grocery bill of \u20b9{amount}.")
    return redirect('bill_list')


@login_required
def extra_list(request):
    c = open_cycle()
    extras = _extras_for(c)
    form = ExtraGroceryForm(cycle=c) if c else ExtraGroceryForm()
    return render(request, 'groceries/extra_list.html', _extra_ctx(c, extras, form, None, False))


@login_required
def extra_add(request):
    c = open_cycle()
    if not c:
        messages.error(request, "Open a cycle in Cycles admin before logging extras.")
        return redirect('extra_list')
    form = ExtraGroceryForm(request.POST, cycle=c)
    if form.is_valid():
        extra = form.save(commit=False)
        extra.cycle = c
        extra.save()
        messages.success(request, f"Extra grocery '{extra.product_name}' saved.")
        return redirect('extra_list')
    return render(request, 'groceries/extra_list.html', _extra_ctx(c, _extras_for(c), form, None, False))


@login_required
def extra_edit(request, extra_id):
    extra = get_object_or_404(ExtraGrocery, pk=extra_id)
    c = extra.cycle
    form = ExtraGroceryForm(request.POST or None, instance=extra, cycle=c)
    return render(request, 'groceries/extra_list.html', _extra_ctx(c, _extras_for(c), form, extra, True))


@login_required
def extra_update(request, extra_id):
    extra = get_object_or_404(ExtraGrocery, pk=extra_id)
    c = extra.cycle
    form = ExtraGroceryForm(request.POST, instance=extra, cycle=c)
    if form.is_valid():
        form.save()
        messages.success(request, "Extra grocery entry updated.")
        return redirect('extra_list')
    return render(request, 'groceries/extra_list.html', _extra_ctx(c, _extras_for(c), form, extra, True))


@login_required
def extra_delete(request, extra_id):
    extra = get_object_or_404(ExtraGrocery, pk=extra_id)
    if request.method == 'POST':
        name = extra.product_name
        extra.delete()
        messages.success(request, f"Deleted '{name}'.")
    return redirect('extra_list')


def _bills_for(cycle):
    if not cycle:
        return GroceryBill.objects.none()
    return (
        GroceryBill.objects
        .select_related('purchased_by')
        .prefetch_related('items')
        .filter(cycle=cycle)
        .order_by('-bill_date')
    )


def _extras_for(cycle):
    if not cycle:
        return ExtraGrocery.objects.none()
    return (
        ExtraGrocery.objects
        .select_related('purchased_by')
        .filter(cycle=cycle)
        .order_by('-purchase_date')
    )


def _ctx(cycle, bills, form, editing_bill, editing):
    return {
        'current_cycle': cycle,
        'has_cycle': cycle is not None,
        'bills': bills,
        'bill_form': form,
        'editing_bill': editing_bill,
        'is_editing': editing,
        'member_options': member_choices_json(cycle),
    }


def _extra_ctx(cycle, extras, form, editing_extra, editing):
    return {
        'current_cycle': cycle,
        'has_cycle': cycle is not None,
        'extras': extras,
        'extra_form': form,
        'editing_extra': editing_extra,
        'is_editing': editing,
        'member_options': member_choices_json(cycle),
    }


def _mismatch_note(request, bill):
    if bill.total_mismatch:
        items_total = bill.items_total()
        messages.info(
            request,
            f"Itemized total (\u20b9{items_total}) differs from total_amount (\u20b9{bill.total_amount}); total_amount kept as authoritative.",
        )
