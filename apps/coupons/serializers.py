from rest_framework import serializers
from apps.coupons.models import Coupon


class CouponApplySerializer(serializers.Serializer):
    code = serializers.CharField(required=True, help_text="Coupon code to validate and apply.")
    cart_subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, required=True, help_text="Current cart subtotal.")


class CouponResponseSerializer(serializers.ModelSerializer):
    discount_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Coupon
        fields = ['id', 'code', 'discount_type', 'discount_value', 'min_order_amount', 'description', 'discount_amount']
