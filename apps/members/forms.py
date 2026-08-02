from datetime import date
from decimal import Decimal

from django import forms

from .models import Member, MemberCycle

INPUT_CLASS = 'form-input'
SELECT_CLASS = 'form-select'
TEXTAREA_CLASS = 'form-textarea'


class AddMemberForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'e.g. Alice'}),
    )
    join_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': INPUT_CLASS, 'type': 'date'}, format='%Y-%m-%d'),
    )
    deposit_amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        initial=Decimal('0'),
        widget=forms.NumberInput(attrs={'class': INPUT_CLASS, 'step': '0.01', 'placeholder': '0.00'}),
    )

    def __init__(self, *args, **kwargs):
        initial_join_date = kwargs.pop('initial_join_date', None)
        super().__init__(*args, **kwargs)
        if initial_join_date:
            self.fields['join_date'].initial = initial_join_date


class EditMemberForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'e.g. Alice'}),
    )
    join_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'class': INPUT_CLASS, 'type': 'date'}, format='%Y-%m-%d'),
    )
    deposit_amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        initial=Decimal('0'),
        widget=forms.NumberInput(attrs={'class': INPUT_CLASS, 'step': '0.01', 'min': '0'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
