from django.contrib import admin
from .models import Cycle


@admin.register(Cycle)
class CycleAdmin(admin.ModelAdmin):
    list_display = ('label', 'start_date', 'end_date', 'status', 'created_at')
    list_filter = ('status', 'start_date')
    search_fields = ('label',)
    readonly_fields = ('created_at',)
