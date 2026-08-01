from datetime import date

from django import forms

from .models import FixedBill

INPUT_CLASS = 'form-input'
SELECT_CLASS = 'form-select'
TEXTAREA_CLASS = 'form-textarea'


class FixedBillForm(forms.ModelForm):
    class Meta:
        model = FixedBill
        fields = ['bill_type', 'amount', 'bill_date', 'description']
        widgets = {
            'bill_type': forms.Select(attrs={'class': SELECT_CLASS}),
            'amount': forms.NumberInput(
                attrs={'class': INPUT_CLASS, 'step': '0.01', 'placeholder': '0.00'}
            ),
            'bill_date': forms.DateInput(
                attrs={'class': INPUT_CLASS, 'type': 'date'}, format='%Y-%m-%d'
            ),
            'description': forms.Textarea(
                attrs={
                    'class': TEXTAREA_CLASS, 'rows': 2,
                    'placeholder': 'e.g. Internet provider, generator fuel, building rental...',
                }
            ),
        }
        labels = {
            'bill_type': 'Bill Type',
            'amount': 'Amount',
            'bill_date': 'Date',
            'description': 'Description',
        }
        help_texts = {
            'description': 'Required when Bill Type is "Other".',
        }

    def __init__(self, *args, cycle=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._cycle = cycle
        if not self.initial.get('bill_date'):
            self.fields['bill_date'].initial = date.today()
        self.fields['amount'].widget.attrs['step'] = '0.01'

    def clean(self):
        cleaned = super().clean()
        amount = cleaned.get('amount')
        if amount is not None and amount <= 0:
            self.add_error('amount', 'Amount must be greater than zero.')
        return cleaned
