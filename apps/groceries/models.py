from decimal import Decimal, ROUND_HALF_UP

from django.db import models


class GroceryBill(models.Model):
    cycle = models.ForeignKey(
        'cycles.Cycle',
        on_delete=models.CASCADE,
        related_name='grocery_bills',
    )
    bill_date = models.DateField()
    purchased_by = models.ForeignKey(
        'members.Member',
        on_delete=models.CASCADE,
        related_name='grocery_bills',
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-bill_date']
        indexes = [
            models.Index(fields=['cycle', '-bill_date']),
        ]

    def __str__(self):
        return f"Bill — {self.cycle.label} — {self.bill_date}"

    def items_total(self):
        agg = self.items.aggregate(total=models.Sum('line_total'))
        total = agg['total']
        return total if total is not None else Decimal('0')

    @property
    def total_mismatch(self):
        if not self.items.exists():
            return False
        return abs(self.items_total() - (self.total_amount or Decimal('0'))) > Decimal('0.01')


class GroceryBillItem(models.Model):
    grocery_bill = models.ForeignKey(
        GroceryBill,
        on_delete=models.CASCADE,
        related_name='items',
    )
    item_name = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=10, decimal_places=3)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.line_total = (self.quantity or Decimal('0')) * (self.unit_price or Decimal('0'))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item_name} ({self.quantity} × {self.unit_price})"


class ExtraGrocery(models.Model):
    cycle = models.ForeignKey(
        'cycles.Cycle',
        on_delete=models.CASCADE,
        related_name='extra_groceries',
    )
    purchased_by = models.ForeignKey(
        'members.Member',
        on_delete=models.CASCADE,
        related_name='extra_groceries',
    )
    product_name = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=10, decimal_places=3)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateField()

    class Meta:
        ordering = ['-purchase_date']
        indexes = [
            models.Index(fields=['cycle', '-purchase_date']),
        ]

    def __str__(self):
        return f"{self.product_name} — {self.purchase_date}"

    @property
    def line_total(self):
        if self.quantity is None or self.price is None:
            return Decimal('0')
        return (self.quantity * self.price).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
