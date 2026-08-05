from django.core.exceptions import ValidationError
from django.db import models


class Cycle(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
    ]

    label = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    fixed_member_rate = models.DecimalField(max_digits=10, decimal_places=2, default=30)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']
        constraints = [
            models.UniqueConstraint(
                fields=['status'],
                condition=models.Q(status='open'),
                name='unique_open_cycle',
            ),
        ]

    def __str__(self):
        return self.label

    def clean(self):
        if self.status == 'open':
            existing = Cycle.objects.filter(status='open').exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError(
                    'Close the current open cycle before opening a new one.'
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
