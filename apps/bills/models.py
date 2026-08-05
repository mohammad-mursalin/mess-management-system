from django.core.exceptions import ValidationError
from django.db import models


class FixedBill(models.Model):
    BILL_TYPE_CHOICES = [
        ('electricity', 'Electricity'),
        ('chef', 'Chef'),
        ('wifi', 'Wifi'),
        ('gas', 'Gas'),
        ('garbage', 'Garbage'),
        ('other', 'Other'),
    ]

    cycle = models.ForeignKey(
        'cycles.Cycle',
        on_delete=models.CASCADE,
        related_name='fixed_bills',
    )
    bill_type = models.CharField(
        max_length=20,
        choices=BILL_TYPE_CHOICES,
        default='other',
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    bill_date = models.DateField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-bill_date']
        indexes = [
            models.Index(fields=['cycle', 'bill_type']),
            models.Index(fields=['cycle', '-bill_date']),
        ]

    def __str__(self):
        return f"{self.get_bill_type_display()} — {self.cycle.label} — {self.bill_date}"

    def clean(self):
        """
        Enforced at the model level (backend-spec.md §7) so it applies in both
        the custom manager form and Django admin:
        - bill_type 'other' requires a non-empty description.
        - amount must be greater than zero.
        """
        if self.amount is not None and self.amount <= 0:
            raise ValidationError({'amount': 'Amount must be greater than zero.'})

        if self.bill_type == 'other':
            if not self.description or not self.description.strip():
                raise ValidationError(
                    {'description': 'A description is required when bill type is "Other".'}
                )
