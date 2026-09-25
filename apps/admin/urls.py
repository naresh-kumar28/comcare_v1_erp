from django.urls import path
from . import views

urlpatterns = [
    # Dashboard & General Views
    path('', views.admin_dashboard, name='admin_dashboard'),
    # Orders Module Routes & HTMX Endpoints
    path('orders/', views.admin_orders, name='admin_orders'),
    path('orders/detail/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),
    path('orders/update-status/<int:order_id>/', views.admin_order_update_status, name='admin_order_update_status'),

    # Products Module Routes & HTMX Endpoints
    path('products/', views.admin_products, name='admin_products'),
    path('products/form/', views.admin_product_get_form, name='admin_product_get_form'),
    path('products/form/<int:product_id>/', views.admin_product_get_form, name='admin_product_edit_form'),
    path('products/save/', views.admin_product_save, name='admin_product_save'),
    path('products/delete/<int:product_id>/', views.admin_product_delete, name='admin_product_delete'),
    path('products/gallery/delete/<int:image_id>/', views.admin_product_gallery_image_delete, name='admin_product_gallery_image_delete'),
    path('products/toggle/<int:product_id>/<str:flag>/', views.admin_product_toggle_flag, name='admin_product_toggle_flag'),

    # Categories Module Routes & HTMX Endpoints
    path('categories/', views.admin_categories, name='admin_categories'),
    path('categories/form/', views.admin_category_get_form, name='admin_category_get_form'),
    path('categories/form/<int:category_id>/', views.admin_category_get_form, name='admin_category_edit_form'),
    path('categories/save/', views.admin_category_save, name='admin_category_save'),
    path('categories/delete/<int:category_id>/', views.admin_category_delete, name='admin_category_delete'),

    # Inventory Module Routes & HTMX Endpoints
    path('inventory/', views.admin_inventory, name='admin_inventory'),
    path('inventory/metrics/', views.admin_inventory_metrics, name='admin_inventory_metrics'),
    path('inventory/update-stock/<int:product_id>/', views.admin_inventory_update_stock, name='admin_inventory_update_stock'),
    # Customers Module Routes & HTMX Endpoints
    path('customers/', views.admin_customers, name='admin_customers'),
    path('customers/detail/<int:user_id>/', views.admin_customer_detail, name='admin_customer_detail'),
    path('returns/', views.admin_returns, name='admin_returns'),
    # Coupons Module Routes & HTMX Endpoints
    path('coupons/', views.admin_coupons, name='admin_coupons'),
    path('coupons/form/', views.admin_coupon_get_form, name='admin_coupon_get_form'),
    path('coupons/form/<int:coupon_id>/', views.admin_coupon_get_form, name='admin_coupon_edit_form'),
    path('coupons/save/', views.admin_coupon_save, name='admin_coupon_save'),
    path('coupons/delete/<int:coupon_id>/', views.admin_coupon_delete, name='admin_coupon_delete'),
    path('coupons/toggle/<int:coupon_id>/', views.admin_coupon_toggle_active, name='admin_coupon_toggle_active'),
    # Services Module Routes & HTMX Endpoints
    path('services/', views.admin_services, name='admin_services'),
    path('services/update-status/<int:lead_id>/', views.admin_service_update_status, name='admin_service_update_status'),
    path('services/delete/<int:lead_id>/', views.admin_service_delete, name='admin_service_delete'),
    path('reports/', views.admin_reports, name='admin_reports'),
]
