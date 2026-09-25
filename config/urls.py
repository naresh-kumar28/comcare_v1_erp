"""
URL configuration for ComCare ERP project.
Routes both existing template-rendered pages and new REST API v1 endpoints.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from apps.accounts.views import SecureOrderInvoiceView
from apps.core.views import health

# REST API v1 routes
api_v1_patterns = [
    path('auth/', include('apps.accounts.api_urls')),
    path('categories/', include('apps.categories.api_urls')),
    path('products/', include('apps.store.api_urls')),
    path('', include('apps.cart.api_urls')),
    path('coupons/', include('apps.coupons.api_urls')),
    path('payments/', include('apps.payments.api_urls')),
]

urlpatterns = [
    # Health Check
    path('health/', health, name='health'),

    # Django Admin Panel
    path('admin/', admin.site.urls),

    # Secure Invoice Endpoint
    path('invoice/<str:order_number>/<uuid:token>/', SecureOrderInvoiceView.as_view(), name='secure_order_invoice'),

    # OpenAPI 3 Schema & Interactive API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # REST API v1 Root
    path('api/v1/', include(api_v1_patterns)),

    # Legacy / Parallel HTML Template & HTMX Views
    path('', include('apps.core.urls')),
    path('account/', include('apps.accounts.urls')),
    path('store/', include('apps.store.urls')),
    path('services/', include('apps.services.urls')),
    path('cart/', include('apps.cart.urls')),
    path('coupons/', include('apps.coupons.urls')),
    path('admin-panel/', include('apps.admin.urls')),
    path('reviews/', include('apps.reviews.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
