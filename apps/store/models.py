from decimal import Decimal
from django.db import models
from django.conf import settings
from apps.categories.models import Category

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=350, unique=True, blank=True)
    sku = models.CharField(max_length=100, unique=True)
    hsn_code = models.CharField(max_length=20, default='8471', blank=True, verbose_name='HSN/SAC Code')
    barcode = models.CharField(max_length=100, blank=True, null=True)
    brand = models.CharField(max_length=120)
    short_description = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    original_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2)

    is_sale = models.BooleanField(default=False)
    discount_percent = models.PositiveSmallIntegerField(blank=True, null=True)

    stock_qty = models.PositiveIntegerField(default=0)

    image = models.ImageField(upload_to='store_products/%Y-%m-%d', blank=True, null=True)
    # image_icon = models.CharField(max_length=50, blank=True)

    # ==========================
    # Technical Specifications
    # ==========================

    processor = models.CharField(max_length=120, blank=True)
    processor_short = models.CharField(max_length=80, blank=True, default="")

    ram = models.CharField(max_length=120, blank=True)
    ram_short = models.CharField(max_length=80, blank=True, default="")

    storage = models.CharField(max_length=120, blank=True)
    storage_short = models.CharField(max_length=80, blank=True, default="")

    graphics = models.CharField(max_length=120, blank=True)
    graphics_short = models.CharField(max_length=80, blank=True, default="")

    display = models.CharField(max_length=120, blank=True)
    display_short = models.CharField(max_length=80, blank=True, default="")

    battery = models.CharField(max_length=120, blank=True)
    battery_short = models.CharField(max_length=80, blank=True, default="")

    warranty = models.CharField(max_length=120, blank=True)
    warranty_short = models.CharField(max_length=80, blank=True, default="")

    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    reviews_count = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=False)
    is_best_seller = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.original_price and self.original_price > Decimal('0'):
            self.discount_percent = int(
                round(
                    (self.original_price - self.selling_price)
                    / self.original_price * 100
                )
            )
            self.is_sale = self.discount_percent > 0
        else:
            self.discount_percent = None
            self.is_sale = False

        super().save(*args, **kwargs)

    @property
    def stock_status(self):
        if self.stock_qty <= 0:
            return 'out_of_stock'
        if self.stock_qty <= 5:
            return 'low_stock'
        return 'in_stock'

    @property
    def is_in_stock(self):
        return self.stock_qty > 0

    @property
    def final_price(self):
        # Alias of the effective (discounted) selling price.
        return self.selling_price


class RecentlyViewedProduct(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recently_viewed_products',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='viewed_by',
    )
    viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-viewed_at']
        verbose_name_plural = 'Recently Viewed Products'

    def __str__(self):
        return f"{self.user} → {self.product.title}"


class ProductGalleryImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='store_products/gallery/%Y-%m-%d')
    alt_text = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = 'Product Gallery Images'

    def __str__(self):
        return f"{self.product.title} - Gallery #{self.id}"


class Wishlist(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wishlist_items',
        blank=True,
        null=True,
    )
    session_key = models.CharField(max_length=40, blank=True, null=True)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='in_wishlists',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Wishlist Items'

    def __str__(self):
        return f"{self.user or self.session_key} - {self.product.title}"


class FailedSearchLog(models.Model):
    search_query = models.CharField(max_length=255)
    city = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    searched_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='failed_searches'
    )

    class Meta:
        ordering = ['-searched_at']
        verbose_name = 'Failed Search Log'
        verbose_name_plural = 'Failed Search Logs'

    def __str__(self):
        return f"{self.search_query} ({self.ip_address or 'Unknown IP'})"
