from django.urls import path
from . import views

urlpatterns = [
    # User-Facing Frontend Routes
    path('', views.home, name='home'),
    path('categories/', views.categories, name='categories'),
    path('search/', views.search, name='search'),
    

    # Information & Policy Routes
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms/', views.terms, name='terms'),
    path('refund-policy/', views.refund_policy, name='refund_policy'),
    path('404/', views.page_not_found_view, name='404'),
    path('500/', views.server_error_view, name='500'),
]