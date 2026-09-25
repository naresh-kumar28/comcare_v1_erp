from django.contrib import admin

from .models import Coupon


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = [
        'code',
        'discount_type',
        'discount_value',
        'min_order_amount',
        'used_count',
        'usage_limit',
        'valid_from',
        'valid_to',
        'is_active',
    ]
    list_filter = ['is_active', 'discount_type']
    search_fields = ['code', 'description']
    list_editable = ['is_active']
    readonly_fields = ['used_count', 'created_at', 'updated_at']
