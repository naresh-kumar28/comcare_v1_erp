from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from apps.accounts.views import (
    AccountOrdersView,
    AddressesView,
    CancelOrderView,
    DashboardView,
    OrderInvoiceView,
    ProfileView,
    RemoveFromWishlistView,
    ToggleWishlistView,
    UserRegisterView,
    WishlistView,
)

urlpatterns = [
    # ----------------------------------------------------
    # User Registration (CBV)
    # ----------------------------------------------------
    path('register/', UserRegisterView.as_view(), name='register'),

    # ----------------------------------------------------
    # Django Built-in Authentication Views (auth_views)
    # ----------------------------------------------------
    path('login/', auth_views.LoginView.as_view(
        template_name='login.html',
        redirect_authenticated_user=True
    ), name='login'),

    path('logout/', auth_views.LogoutView.as_view(
        next_page='login',
        http_method_names=['get', 'post']
    ), name='logout'),

    # Password Change Workflow
    path('change-password/', auth_views.PasswordChangeView.as_view(
        template_name='change_password.html',
        success_url=reverse_lazy('password_change_done')
    ), name='change_password'),

    path('change-password/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='registration/password_change_done.html'
    ), name='password_change_done'),

    # Password Reset / Forgot Password Workflow
    path('forgot-password/', auth_views.PasswordResetView.as_view(
        template_name='forgot_password.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt',
        success_url=reverse_lazy('password_reset_done')
    ), name='forgot_password'),

    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='forgot_password.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt',
        success_url=reverse_lazy('password_reset_done')
    ), name='password_reset'),

    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url=reverse_lazy('password_reset_complete')
    ), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),

    # ----------------------------------------------------
    # User Account Dashboard & Features (CBVs)
    # ----------------------------------------------------
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('orders/', AccountOrdersView.as_view(), name='account_orders'),
    path('orders/cancel/', CancelOrderView.as_view(), name='cancel_order'),
    path('orders/cancel/<int:order_id>/', CancelOrderView.as_view(), name='cancel_order_direct'),
    path('orders/<int:order_id>/invoice/', OrderInvoiceView.as_view(), name='order_invoice'),
    
    path('wishlist/', WishlistView.as_view(), name='wishlist'),
    path('wishlist/remove/<int:product_id>/', RemoveFromWishlistView.as_view(), name='remove_from_wishlist'),
    path('wishlist/toggle/<int:product_id>/', ToggleWishlistView.as_view(), name='toggle_wishlist'),
    
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/update/', ProfileView.as_view(), name='update_profile'),
    path('addresses/', AddressesView.as_view(), name='addresses'),
]
