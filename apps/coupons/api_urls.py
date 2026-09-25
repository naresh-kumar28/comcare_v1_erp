from django.urls import path
from apps.coupons.api_views import ApplyCouponAPIView, RemoveCouponAPIView

urlpatterns = [
    path('apply/', ApplyCouponAPIView.as_view(), name='api_coupon_apply'),
    path('remove/', RemoveCouponAPIView.as_view(), name='api_coupon_remove'),
]
