from django.contrib import admin
from .models import Tenant, SubscriptionPayment, TenantSyncLog


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'subscription_status', 'days_left', 'monthly_fee', 'is_active', 'subscription_expires_at')
    list_filter = ('is_active', 'subscription_expires_at')
    search_fields = ('name', 'slug', 'owner_name', 'phone', 'bot_username')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(SubscriptionPayment)
class SubscriptionPaymentAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'amount', 'paid_at', 'days_added', 'payment_method', 'receipt_number')
    list_filter = ('payment_method', 'paid_at')
    search_fields = ('tenant__name', 'receipt_number', 'comment')


@admin.register(TenantSyncLog)
class TenantSyncLogAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'status_code', 'response_time_ms', 'is_healthy', 'synced_at')
    list_filter = ('is_healthy', 'status_code')
    search_fields = ('tenant__name', 'error_message')
