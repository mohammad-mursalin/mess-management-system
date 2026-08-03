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

    def __str__(self):
        return self.label
