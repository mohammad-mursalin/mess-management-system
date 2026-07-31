from cycles.models import Cycle


def current_cycle(request):
    cycle = Cycle.objects.filter(status='open').first()
    return {'current_cycle': cycle}
