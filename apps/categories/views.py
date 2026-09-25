from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from apps.categories.models import Category
from apps.categories.serializers import CategorySerializer
from common.permissions import IsAdminOrReadOnly


class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for listing, retrieving, creating, updating, and deleting categories.
    Read-only for unauthenticated / regular users; write access restricted to staff/admin.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        queryset = super().get_queryset()
        # If user is not staff, only return active categories
        if not (self.request.user and self.request.user.is_authenticated and self.request.user.is_staff):
            queryset = queryset.filter(is_active=True)
        return queryset
