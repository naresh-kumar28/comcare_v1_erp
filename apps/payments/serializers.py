from rest_framework import serializers


class RazorpayCreateOrderSerializer(serializers.Serializer):
    order_number = serializers.CharField(required=True, help_text="Order number to generate Razorpay gateway order for.")


class RazorpayVerifyPaymentSerializer(serializers.Serializer):
    order_number = serializers.CharField(required=True)
    razorpay_order_id = serializers.CharField(required=True)
    razorpay_payment_id = serializers.CharField(required=True)
    razorpay_signature = serializers.CharField(required=True)
