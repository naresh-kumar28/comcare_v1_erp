from rest_framework import serializers
from apps.cart.models import Cart, CartItem, UserAddress, ShippingConfig, Order, OrderItem
from apps.store.models import Product
from apps.store.serializers import ProductListSerializer


class CartProductSummarySerializer(serializers.ModelSerializer):
    is_in_stock = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'slug', 'image', 'selling_price', 'stock_qty', 'is_in_stock']


class CartItemSerializer(serializers.ModelSerializer):
    product = CartProductSummarySerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        source='product',
        queryset=Product.objects.filter(is_active=True),
        write_only=True
    )
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'unit_price', 'total_price', 'added_at']
        read_only_fields = ['id', 'unit_price', 'total_price', 'added_at']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    tax = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    coupon_code = serializers.CharField(read_only=True, allow_null=True)
    coupon_discount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    shipping_cost = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    grand_total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = [
            'id', 'user', 'session_key', 'items', 'subtotal',
            'total_items', 'tax', 'coupon_code', 'coupon_discount',
            'shipping_cost', 'grand_total', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'session_key', 'updated_at']


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = [
            'id', 'full_name', 'phone', 'email',
            'address_line1', 'address_line2', 'city', 'state',
            'pincode', 'address_type', 'is_default', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ShippingConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingConfig
        fields = ['flat_rate', 'free_shipping_threshold', 'is_active']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_title', 'quantity', 'unit_price', 'total_price']


class OrderListSerializer(serializers.ModelSerializer):
    total_items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'created_at', 'full_name',
            'payment_method', 'payment_status', 'order_status',
            'grand_total', 'total_items'
        ]

    def get_total_items(self, obj):
        return sum(item.quantity for item in obj.items.all())


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'invoice_access_token', 'full_name',
            'phone', 'email', 'address_line1', 'address_line2',
            'city', 'state', 'pincode', 'subtotal', 'tax',
            'coupon_code', 'coupon_discount', 'shipping_cost', 'grand_total',
            'payment_method', 'payment_status', 'order_status',
            'razorpay_order_id', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'order_number', 'invoice_access_token', 'created_at', 'updated_at']


class OrderCreateSerializer(serializers.Serializer):
    address_id = serializers.IntegerField(required=False, allow_null=True)
    
    # Inline address fields if address_id not supplied
    full_name = serializers.CharField(required=False, max_length=100)
    phone = serializers.CharField(required=False, max_length=20)
    email = serializers.EmailField(required=False, allow_blank=True)
    address_line1 = serializers.CharField(required=False, max_length=255)
    address_line2 = serializers.CharField(required=False, allow_blank=True, max_length=255)
    city = serializers.CharField(required=False, default='Purnea')
    state = serializers.CharField(required=False, default='Bihar')
    pincode = serializers.CharField(required=False, max_length=10)

    payment_method = serializers.ChoiceField(choices=['cod', 'razorpay'], default='cod')
    coupon_code = serializers.CharField(required=False, allow_blank=True)
