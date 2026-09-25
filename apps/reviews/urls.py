from django.urls import path
from .import views

urlpatterns = [
    path('submit/<int:product_id>/', views.submit_review, name='submit_review'),
    path('edit/<int:review_id>/', views.edit_review, name='edit_review'),
    path('delete/<int:review_id>/', views.delete_review, name='delete_review'),
    path('load-more/<int:product_id>/', views.load_more_reviews, name='load_more_reviews'),
]
