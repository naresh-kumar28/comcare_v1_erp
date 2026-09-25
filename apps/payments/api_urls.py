from django.urls import path
from apps.payments.api_views import (
    RazorpayCreateOrderAPIView,
    RazorpayVerifyPaymentAPIView,
    RazorpayWebhookAPIView,
)

urlpatterns = [
    path('razorpay/create-order/', RazorpayCreateOrderAPIView.as_view(), name='api_razorpay_create_order'),
    path('razorpay/verify/', RazorpayVerifyPaymentAPIView.as_view(), name='api_razorpay_verify'),
    path('razorpay/webhook/', RazorpayWebhookAPIView.as_view(), name='api_razorpay_webhook'),
]
