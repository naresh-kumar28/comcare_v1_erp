from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema

from apps.store.models import Product
from apps.store.serializers import ProductListSerializer, ProductDetailSerializer
from apps.store.filters import ProductFilter
from common.permissions import IsAdminOrReadOnly


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing, retrieving, creating, updating, and deleting products.
    Lookup by product slug (e.g. GET /api/v1/products/{slug}/).
    """
    queryset = Product.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['title', 'description', 'brand', 'sku', 'processor', 'ram']
    ordering_fields = ['selling_price', 'rating', 'created_at', 'stock_qty']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action in ['retrieve', 'create', 'update', 'partial_update']:
            return ProductDetailSerializer
        return ProductListSerializer

    def get_queryset(self):
        queryset = Product.objects.select_related('category').prefetch_related('gallery_images').all()
        # Non-staff users can only see active products
        if not (self.request.user and self.request.user.is_authenticated and self.request.user.is_staff):
            queryset = queryset.filter(is_active=True)
        return queryset

    @extend_schema(responses={200: ProductListSerializer(many=True)})
    @action(detail=False, methods=['get'], url_path='featured')
    def featured(self, request):
        """
        GET /api/v1/products/featured/
        Returns a paginated list of featured active products.
        """
        featured_products = self.get_queryset().filter(is_featured=True)
        page = self.paginate_queryset(featured_products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = ProductListSerializer(featured_products, many=True, context={'request': request})
        return Response({'success': True, 'results': serializer.data})

    @extend_schema(responses={200: ProductListSerializer(many=True)})
    @action(detail=False, methods=['get'], url_path='new-arrivals')
    def new_arrivals(self, request):
        """
        GET /api/v1/products/new-arrivals/
        Returns a paginated list of new arrival active products.
        """
        new_arrivals = self.get_queryset().filter(is_new_arrival=True)
        page = self.paginate_queryset(new_arrivals)
        if page is not None:
            serializer = ProductListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = ProductListSerializer(new_arrivals, many=True, context={'request': request})
        return Response({'success': True, 'results': serializer.data})

    @extend_schema(responses={200: ProductListSerializer(many=True)})
    @action(detail=False, methods=['get'], url_path='best-sellers')
    def best_sellers(self, request):
        """
        GET /api/v1/products/best-sellers/
        Returns a paginated list of best seller active products.
        """
        best_sellers = self.get_queryset().filter(is_best_seller=True)
        page = self.paginate_queryset(best_sellers)
        if page is not None:
            serializer = ProductListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = ProductListSerializer(best_sellers, many=True, context={'request': request})
        return Response({'success': True, 'results': serializer.data})
