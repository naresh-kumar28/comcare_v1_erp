from django.urls import path
from apps.cart.api_views import (
    CartAPIView,
    CartItemAddAPIView,
    CartItemUpdateDeleteAPIView,
    CartMergeAPIView,
    UserAddressListCreateAPIView,
    UserAddressDetailAPIView,
    UserAddressSetDefaultAPIView,
    ShippingConfigAPIView,
    OrderListCreateAPIView,
    OrderDetailAPIView,
    OrderCancelAPIView,
    OrderInvoiceAPIView,
)

urlpatterns = [
    # Cart endpoints
    path('cart/', CartAPIView.as_view(), name='api_cart_detail'),
    path('cart/items/', CartItemAddAPIView.as_view(), name='api_cart_item_add'),
    path('cart/items/<int:pk>/', CartItemUpdateDeleteAPIView.as_view(), name='api_cart_item_detail'),
    path('cart/merge/', CartMergeAPIView.as_view(), name='api_cart_merge'),

    # Address endpoints
    path('addresses/', UserAddressListCreateAPIView.as_view(), name='api_addresses_list_create'),
    path('addresses/<int:pk>/', UserAddressDetailAPIView.as_view(), name='api_address_detail'),
    path('addresses/<int:pk>/set-default/', UserAddressSetDefaultAPIView.as_view(), name='api_address_set_default'),

    # Shipping Config
    path('shipping-config/', ShippingConfigAPIView.as_view(), name='api_shipping_config'),

    # Order endpoints
    path('orders/', OrderListCreateAPIView.as_view(), name='api_orders_list_create'),
    path('orders/<str:order_number>/', OrderDetailAPIView.as_view(), name='api_order_detail'),
    path('orders/<int:pk>/cancel/', OrderCancelAPIView.as_view(), name='api_order_cancel'),
    path('orders/<str:order_number>/invoice/', OrderInvoiceAPIView.as_view(), name='api_order_invoice'),
]
