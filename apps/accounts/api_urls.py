from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.api_views import (
    RegisterAPIView,
    LoginAPIView,
    LogoutAPIView,
    UserProfileAPIView,
    PasswordChangeAPIView,
    PasswordResetAPIView,
    PasswordResetConfirmAPIView,
)

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='api_auth_register'),
    path('login/', LoginAPIView.as_view(), name='api_auth_login'),
    path('refresh/', TokenRefreshView.as_view(), name='api_auth_refresh'),
    path('logout/', LogoutAPIView.as_view(), name='api_auth_logout'),
    path('me/', UserProfileAPIView.as_view(), name='api_auth_me'),
    path('password/change/', PasswordChangeAPIView.as_view(), name='api_auth_password_change'),
    path('password/reset/', PasswordResetAPIView.as_view(), name='api_auth_password_reset'),
    path('password/reset/confirm/', PasswordResetConfirmAPIView.as_view(), name='api_auth_password_reset_confirm'),
]
