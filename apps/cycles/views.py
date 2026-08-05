from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404

from apps.cycles.models import Cycle
from apps.cycles.services import update_fixed_member_rate


@login_required
def update_fixed_member_rate(request):
    if request.method == 'POST':
        cycle_id = request.POST.get('cycle_id')
        rate_str = request.POST.get('fixed_member_rate')
        try:
            cycle = Cycle.objects.get(pk=cycle_id)
            rate = float(rate_str)
            if rate < 0:
                raise ValueError
            update_fixed_member_rate(cycle, rate)
            messages.success(request, f"Fixed member rate updated to ৳{rate:.2f}.")
        except (Cycle.DoesNotExist, ValueError):
            messages.error(request, "Invalid rate value.")
    return redirect('month_summary')
