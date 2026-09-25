from rest_framework import serializers
from apps.store.models import Product, ProductGalleryImage
from apps.categories.models import Category
from apps.categories.serializers import CategorySerializer


class ProductGalleryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductGalleryImage
        fields = ['id', 'image', 'alt_text', 'created_at']


class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    category_slug = serializers.ReadOnlyField(source='category.slug')
    stock_status = serializers.ReadOnlyField()
    is_in_stock = serializers.ReadOnlyField()
    final_price = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'sku', 'brand',
            'category', 'category_name', 'category_slug',
            'selling_price', 'original_price', 'final_price',
            'is_sale', 'discount_percent', 'stock_qty',
            'stock_status', 'is_in_stock', 'image',
            'rating', 'reviews_count', 'is_featured',
            'is_new_arrival', 'is_best_seller', 'created_at'
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source='category',
        write_only=True,
        queryset=Category.objects.all()
    )
    gallery_images = ProductGalleryImageSerializer(many=True, read_only=True)
    stock_status = serializers.ReadOnlyField()
    is_in_stock = serializers.ReadOnlyField()
    final_price = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'sku', 'hsn_code', 'barcode', 'brand',
            'category', 'category_id', 'short_description', 'description',
            'original_price', 'selling_price', 'final_price', 'is_sale', 'discount_percent',
            'stock_qty', 'stock_status', 'is_in_stock', 'image',
            'processor', 'processor_short', 'ram', 'ram_short',
            'storage', 'storage_short', 'graphics', 'graphics_short',
            'display', 'display_short', 'battery', 'battery_short',
            'warranty', 'warranty_short', 'rating', 'reviews_count',
            'is_active', 'is_featured', 'is_new_arrival', 'is_best_seller',
            'gallery_images', 'created_at', 'updated_at'
        ]
