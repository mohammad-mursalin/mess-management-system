from django.db import models


class Member(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class MemberCycle(models.Model):
    member = models.ForeignKey('members.Member', on_delete=models.CASCADE, related_name='cycles')
    cycle = models.ForeignKey('cycles.Cycle', on_delete=models.CASCADE, related_name='member_cycles')
    join_date = models.DateField(null=True, blank=True)
    leave_date = models.DateField(null=True, blank=True)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    computed_due = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    settled = models.BooleanField(default=False)

    class Meta:
        unique_together = ('member', 'cycle')
        ordering = ['cycle__start_date', 'member__name']

    def __str__(self):
        return f"{self.member.name} - {self.cycle.label}"

    def save(self, *args, **kwargs):
        if not self.join_date and self.cycle_id:
            from cycles.models import Cycle
            try:
                cycle = Cycle.objects.only('start_date').get(pk=self.cycle_id)
                self.join_date = cycle.start_date
            except Cycle.DoesNotExist:
                pass
        super().save(*args, **kwargs)
