from django.contrib import admin
from .models import MealEntry


@admin.register(MealEntry)
class MealEntryAdmin(admin.ModelAdmin):
    list_display = (
        'member_cycle',
        'entry_date',
        'breakfast',
        'lunch',
        'dinner',
        'updated_by',
        'updated_at',
    )
    list_filter = ('entry_date', 'member_cycle__cycle')
    search_fields = (
        'member_cycle__member__name',
        'member_cycle__cycle__label',
    )
    autocomplete_fields = ('member_cycle', 'updated_by')
    readonly_fields = ('updated_at',)
    date_hierarchy = 'entry_date'
