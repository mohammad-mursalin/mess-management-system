from datetime import date

from django import forms

from apps.members.models import Member, MemberCycle
from .models import GroceryBill, ExtraGrocery


INPUT_CLASS = 'form-input'
SELECT_CLASS = 'form-select'
TEXTAREA_CLASS = 'form-textarea'


def active_member_queryset(cycle):
    if cycle is None:
        return Member.objects.none()
    return Member.objects.filter(
        is_active=True,
        cycles__cycle=cycle,
    ).distinct().order_by('name')


class GroceryBillForm(forms.ModelForm):
    class Meta:
        model = GroceryBill
        fields = ['bill_date', 'purchased_by', 'total_amount', 'note']
        widgets = {
            'bill_date': forms.DateInput(
                attrs={'class': INPUT_CLASS, 'type': 'date'}, format='%Y-%m-%d'
            ),
            'purchased_by': forms.Select(attrs={'class': SELECT_CLASS}),
            'total_amount': forms.NumberInput(
                attrs={'class': INPUT_CLASS, 'step': '0.01', 'placeholder': '0.00'}
            ),
            'note': forms.Textarea(
                attrs={'class': TEXTAREA_CLASS, 'rows': 2,
                       'placeholder': 'Optional note (e.g. store name)'}
            ),
        }
        labels = {
            'bill_date': 'Bill Date',
            'purchased_by': 'Purchased By',
            'total_amount': 'Total Amount',
            'note': 'Note',
        }

    def __init__(self, *args, cycle=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._cycle = cycle
        if not self.initial.get('bill_date'):
            self.fields['bill_date'].initial = date.today()
        self.fields['purchased_by'].queryset = active_member_queryset(cycle)

    def clean(self):
        cleaned = super().clean()
        cycle = self._cycle
        purchased_by = cleaned.get('purchased_by')
        total = cleaned.get('total_amount')
        if total is not None and total <= 0:
            self.add_error('total_amount', 'Total amount must be greater than zero.')
        if cycle and purchased_by:
            if not MemberCycle.objects.filter(
                cycle=cycle, member=purchased_by, member__is_active=True
            ).exists():
                self.add_error('purchased_by', 'Selected member is not active in this cycle.')
        return cleaned


class ExtraGroceryForm(forms.ModelForm):
    class Meta:
        model = ExtraGrocery
        fields = ['purchased_by', 'product_name', 'quantity', 'price', 'purchase_date']
        widgets = {
            'purchased_by': forms.Select(attrs={'class': SELECT_CLASS}),
            'product_name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'e.g. Milk'}),
            'quantity': forms.NumberInput(attrs={'class': INPUT_CLASS, 'step': '0.001', 'placeholder': '1'}),
            'price': forms.NumberInput(attrs={'class': INPUT_CLASS, 'step': '0.01', 'placeholder': '0.00'}),
            'purchase_date': forms.DateInput(
                attrs={'class': INPUT_CLASS, 'type': 'date'}, format='%Y-%m-%d'
            ),
        }
        labels = {
            'purchased_by': 'Purchased By',
            'product_name': 'Product',
            'quantity': 'Quantity',
            'price': 'Price',
            'purchase_date': 'Date',
        }

    def __init__(self, *args, cycle=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._cycle = cycle
        if not self.initial.get('purchase_date'):
            self.fields['purchase_date'].initial = date.today()
        self.fields['quantity'].initial = self.fields['quantity'].initial or 1
        self.fields['purchased_by'].queryset = active_member_queryset(cycle)

    def clean(self):
        cleaned = super().clean()
        cycle = self._cycle
        purchased_by = cleaned.get('purchased_by')
        price = cleaned.get('price')
        quantity = cleaned.get('quantity')
        if price is not None and price <= 0:
            self.add_error('price', 'Price must be greater than zero.')
        if quantity is not None and quantity <= 0:
            self.add_error('quantity', 'Quantity must be greater than zero.')
        if cycle and purchased_by:
            if not MemberCycle.objects.filter(
                cycle=cycle, member=purchased_by, member__is_active=True
            ).exists():
                self.add_error('purchased_by', 'Selected member is not active in this cycle.')
        return cleaned
