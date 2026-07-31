from django.contrib import admin
from .models import Member, MemberCycle


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)
    readonly_fields = ('created_at',)


@admin.register(MemberCycle)
class MemberCycleAdmin(admin.ModelAdmin):
    list_display = ('member', 'cycle', 'join_date', 'leave_date', 'deposit_amount', 'computed_due', 'settled')
    list_filter = ('cycle', 'settled')
    search_fields = ('member__name', 'cycle__label')
    autocomplete_fields = ('member', 'cycle')
