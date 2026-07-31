from decimal import Decimal

from django.db import models
from django.utils import timezone


class MealEntry(models.Model):
    BREAKFAST_CHOICES = [
        (Decimal('0'), '0'),
        (Decimal('0.5'), '½'),
        (Decimal('1'), '1'),
    ]
    LUNCH_CHOICES = [
        (Decimal('0'), '0'),
        (Decimal('1'), '1'),
    ]
    DINNER_CHOICES = LUNCH_CHOICES

    member_cycle = models.ForeignKey(
        'members.MemberCycle',
        on_delete=models.CASCADE,
        related_name='meal_entries',
    )
    entry_date = models.DateField()
    breakfast = models.DecimalField(
        max_digits=3, decimal_places=1,
        choices=BREAKFAST_CHOICES, default=Decimal('0'),
    )
    lunch = models.DecimalField(
        max_digits=3, decimal_places=1,
        choices=LUNCH_CHOICES, default=Decimal('0'),
    )
    dinner = models.DecimalField(
        max_digits=3, decimal_places=1,
        choices=DINNER_CHOICES, default=Decimal('0'),
    )
    updated_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='meal_entries',
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('member_cycle', 'entry_date')
        ordering = ['entry_date', 'member_cycle__member__name']
        indexes = [
            models.Index(fields=['entry_date']),
        ]

    def __str__(self):
        return f"{self.member_cycle.member.name} - {self.entry_date}"

    def is_editable(self):
        cycle = self.member_cycle.cycle
        if cycle.status == 'closed':
            return False
        return cycle.start_date <= timezone.now().date()

    def clean(self):
        from django.core.exceptions import ValidationError

        cycle = self.member_cycle.cycle
        mc = self.member_cycle

        if cycle.status == 'closed':
            raise ValidationError(
                f"Cannot add entries to a closed cycle ({cycle.label})."
            )

        cycle_start = cycle.start_date
        cycle_end = cycle.end_date or timezone.now().date()

        if self.entry_date < cycle_start or self.entry_date > cycle_end:
            if cycle.end_date:
                raise ValidationError(
                    f"Entry date {self.entry_date} is outside cycle "
                    f"{cycle.label} ({cycle_start} to {cycle_end})."
                )
            raise ValidationError(
                f"Entry date {self.entry_date} is before the cycle start date "
                f"({cycle_start})."
            )

        if self.entry_date < mc.join_date:
            raise ValidationError(
                f"Member joined on {mc.join_date}; cannot log meals before that date."
            )

        if mc.leave_date and self.entry_date > mc.leave_date:
            raise ValidationError(
                f"Member left on {mc.leave_date}; cannot log meals after that date."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
