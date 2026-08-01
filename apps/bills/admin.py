from django.contrib import admin
from .models import FixedBill


@admin.register(FixedBill)
class FixedBillAdmin(admin.ModelAdmin):
    list_display = (
        'bill_date', 'cycle', 'bill_type', 'amount',
        'description_short', 'created_at',
    )
    list_filter = ('cycle', 'bill_type', 'bill_date')
    search_fields = ('description', 'cycle__label')
    autocomplete_fields = ('cycle',)
    date_hierarchy = 'bill_date'
    list_select_related = ('cycle',)

    def description_short(self, obj):
        return (obj.description or '')[:50] or '—'
    description_short.short_description = 'Description'
