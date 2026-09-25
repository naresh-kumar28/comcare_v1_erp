from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart, name='cart'),
    path('buy-now/<int:product_id>/', views.buy_now, name='buy_now'),
    path('add_cart/<int:product_id>/', views.add_cart, name='add_cart'),
    path('add_cart_ajax/<int:product_id>/', views.add_cart_ajax, name='add_cart_ajax'),
    path('remove_cart/<int:product_id>/', views.remove_cart, name='remove_cart'),
    path('remove_cart_item/<int:product_id>/', views.remove_cart_item, name='remove_cart_item'),

    path('checkout/', views.checkout, name='checkout'),
    path('save-address/', views.save_address, name='save_address'),
    path('get-address/<int:address_id>/', views.get_address_json, name='get_address_json'),
    path('set-default-address/<int:address_id>/', views.set_default_address, name='set_default_address'),
    path('delete-address/<int:address_id>/', views.delete_address, name='delete_address'),
    path('place-order/', views.place_order, name='place_order'),
    path('verify-payment/', views.verify_payment, name='verify_payment'),
    path('order-success/', views.order_success, name='order_success'),
]
