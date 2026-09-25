from django.contrib import admin

from apps.cart.models import Cart, CartItem, Order, OrderItem, ShippingConfig, UserAddress


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_key', 'is_active', 'total_items', 'subtotal', 'created_at', 'updated_at')
    search_fields = ('user__email', 'session_key')
    list_filter = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'unit_price', 'total_price', 'added_at', 'updated_at')
    search_fields = ('product__title', 'cart__user__email')
    readonly_fields = ('added_at', 'updated_at')


@admin.register(ShippingConfig)
class ShippingConfigAdmin(admin.ModelAdmin):
    list_display = ('flat_rate', 'free_shipping_threshold', 'is_active')

    def has_add_permission(self, request):
        return not ShippingConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'phone', 'city', 'state', 'pincode', 'address_type', 'is_default', 'created_at')
    search_fields = ('full_name', 'phone', 'email', 'address_line1', 'city', 'pincode')
    list_filter = ('address_type', 'is_default', 'city', 'state')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_title', 'quantity', 'unit_price', 'total_price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'full_name', 'phone', 'grand_total', 'payment_method', 'payment_status', 'order_status', 'created_at')
    list_filter = ('payment_method', 'payment_status', 'order_status', 'created_at')
    search_fields = ('order_number', 'full_name', 'phone', 'email', 'razorpay_order_id', 'razorpay_payment_id')
    readonly_fields = ('order_number', 'created_at', 'updated_at')
    inlines = [OrderItemInline]


