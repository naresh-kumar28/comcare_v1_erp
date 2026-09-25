from django.contrib import admin
from .models import Product, ProductGalleryImage, FailedSearchLog


class ProductGalleryImageInline(admin.TabularInline):
    model = ProductGalleryImage
    extra = 3


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductGalleryImageInline]
    list_display = (
        'title',
        'sku',
        'hsn_code',
        'brand',
        'category',
        'selling_price',
        'stock_qty',
        'is_active',
        'is_featured',
        'is_best_seller',
        'created_at',
    )

    list_filter = (
        'category',
        'brand',
        'is_active',
        'is_featured',
        'is_new_arrival',
        'is_best_seller',
    )

    search_fields = (
        'title',
        'sku',
        'brand',
        'category__name',
    )

    prepopulated_fields = {
        'slug': ('title',)
    }

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'category',
                'title',
                'slug',
                'sku',
                'barcode',
                'brand',
                'image',
            )
        }),

        ('Description', {
            'fields': (
                'short_description',
                'description',
            )
        }),

        ('Pricing & Stock', {
            'fields': (
                'original_price',
                'selling_price',
                'stock_qty',
            )
        }),

        ('Technical Specifications', {
            'fields': (
                ('processor', 'processor_short'),
                ('ram', 'ram_short'),
                ('storage', 'storage_short'),
                ('graphics', 'graphics_short'),
                ('display', 'display_short'),
                ('battery', 'battery_short'),
                ('warranty', 'warranty_short'),
            ),
            'description': 'Left: Full specification • Right: Highlight value shown on the product page.',
        }),

        ('Flags', {
            'fields': (
                'is_active',
                'is_featured',
                'is_new_arrival',
                'is_best_seller',
            )
        }),

        ('Ratings', {
            'fields': (
                'rating',
                'reviews_count',
            )
        }),
    )

    readonly_fields = (
        'discount_percent',
        'is_sale',
        'created_at',
        'updated_at',
    )


@admin.register(FailedSearchLog)
class FailedSearchLogAdmin(admin.ModelAdmin):
    list_display = (
        'search_query',
        'city',
        'region',
        'country',
        'ip_address',
        'user',
        'searched_at',
    )

    list_filter = (
        'searched_at',
        'city',
        'country',
    )

    search_fields = (
        'search_query',
        'city',
        'region',
        'country',
        'ip_address',
    )

    ordering = ('-searched_at',)

    readonly_fields = (
        'search_query',
        'city',
        'region',
        'country',
        'ip_address',
        'user',
        'searched_at',
    )