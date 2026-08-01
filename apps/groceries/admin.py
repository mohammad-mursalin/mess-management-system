from django.contrib import admin
from .models import GroceryBill, GroceryBillItem, ExtraGrocery


class GroceryBillItemInline(admin.TabularInline):
    model = GroceryBillItem
    extra = 0
    fields = ('item_name', 'quantity', 'unit_price', 'line_total')
    readonly_fields = ('line_total',)
    autocomplete_fields = ()


@admin.register(GroceryBill)
class GroceryBillAdmin(admin.ModelAdmin):
    list_display = ('bill_date', 'cycle', 'purchased_by', 'total_amount', 'item_count', 'created_at')
    list_filter = ('cycle', 'bill_date')
    search_fields = ('note', 'purchased_by__name', 'cycle__label')
    autocomplete_fields = ('purchased_by', 'cycle')
    inlines = [GroceryBillItemInline]
    date_hierarchy = 'bill_date'

    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'


@admin.register(ExtraGrocery)
class ExtraGroceryAdmin(admin.ModelAdmin):
    list_display = ('purchase_date', 'product_name', 'quantity', 'price', 'line_total', 'purchased_by', 'cycle')
    list_filter = ('cycle', 'purchase_date')
    search_fields = ('product_name', 'purchased_by__name', 'cycle__label')
    autocomplete_fields = ('purchased_by', 'cycle')
    date_hierarchy = 'purchase_date'
