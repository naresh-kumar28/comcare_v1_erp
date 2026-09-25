import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models

from apps.store.models import Product


# Cart model ek shopping cart ko represent karta hai.
# Ye registered user ke liye bhi ho sakta hai aur guest user ke liye session_key se bhi track kiya ja sakta hai.
class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carts',
        blank=True,
        null=True,
    )
    # Guest user ke liye session_key store karne ke liye.
    session_key = models.CharField(max_length=40, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name_plural = 'Carts'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['session_key']),
        ]

    def __str__(self):
        return f"Cart #{self.pk} ({self.user.email if self.user else 'Guest'})"

    @property
    def total_items(self):
        # Cart mein kitne total items hain (quantity sum).
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        # Cart ka total amount before kisi discount ya shipping ke.
        return sum(item.total_price for item in self.items.all())

    @property
    def is_guest(self):
        # Agar user None hai to guest cart mana jayega.
        return self.user is None


# CartItem model ek individual product line item ko represent karta hai.
class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items',
    )
    quantity = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    # unit_price store karne se price history preserve rehti hai.
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('cart', 'product')
        ordering = ['added_at']
        verbose_name_plural = 'Cart Items'

    def save(self, *args, **kwargs):
        # Agar unit_price explicitly set nahi hai to product ka selling price use karein.
        if self.unit_price in (None, Decimal('0')):
            self.unit_price = self.product.selling_price
        super().save(*args, **kwargs)

    @property
    def total_price(self):
        # Quantity * unit price kar ke total price nikalein.
        price = self.unit_price if self.unit_price is not None else self.product.selling_price
        return price * self.quantity

    def __str__(self):
        return f"{self.quantity} × {self.product.title} in Cart #{self.cart.pk}"


# ShippingConfig ek singleton model hai jo shipping charges aur free shipping threshold manage karta hai.
# Admin panel se easily configure kiya ja sakta hai.
class ShippingConfig(models.Model):
    flat_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Flat shipping charge (₹). Set 0 for free shipping by default.',
    )
    free_shipping_threshold = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Orders above this subtotal get free shipping. Set 0 to disable threshold-based free shipping.',
    )
    is_active = models.BooleanField(
        default=True,
        help_text='If disabled, shipping is always FREE.',
    )

    class Meta:
        verbose_name = 'Shipping Configuration'
        verbose_name_plural = 'Shipping Configuration'

    def __str__(self):
        return f"Shipping: ₹{self.flat_rate} (Free above ₹{self.free_shipping_threshold})"

    def save(self, *args, **kwargs):
        # Singleton pattern — only one config row allowed.
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # Prevent deletion

    @classmethod
    def get_config(cls):
        """Return the singleton config, creating a default if none exists."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def get_shipping_cost(self, subtotal):
        """Calculate shipping cost based on subtotal."""
        if not self.is_active:
            return Decimal('0.00')
        if self.free_shipping_threshold > 0 and subtotal >= self.free_shipping_threshold:
            return Decimal('0.00')
        return self.flat_rate


class UserAddress(models.Model):
    ADDRESS_TYPES = (
        ('home', 'Home'),
        ('work', 'Work'),
        ('other', 'Other'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='addresses',
        blank=True,
        null=True,
    )
    session_key = models.CharField(max_length=40, blank=True, null=True)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, default='Purnea')
    state = models.CharField(max_length=100, default='Bihar')
    pincode = models.CharField(max_length=10)
    address_type = models.CharField(max_length=20, choices=ADDRESS_TYPES, default='home')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ['-is_default', '-updated_at']
        verbose_name_plural = 'User Addresses'

    def __str__(self):
        return f"{self.full_name} - {self.address_line1}, {self.city} ({self.pincode})"

    def save(self, *args, **kwargs):
        if self.is_default:
            if self.user:
                UserAddress.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
            elif self.session_key:
                UserAddress.objects.filter(session_key=self.session_key, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class Order(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('cod', 'Cash on Delivery'),
        ('razorpay', 'Razorpay Online'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    )

    ORDER_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )

    order_number = models.CharField(max_length=50, unique=True)
    invoice_access_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        blank=True,
        null=True,
    )
    session_key = models.CharField(max_length=40, blank=True, null=True)

    # Shipping details snapshot
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    # Pricing details
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    coupon_code = models.CharField(max_length=50, blank=True, null=True)
    coupon_discount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    grand_total = models.DecimalField(max_digits=12, decimal_places=2)

    # Payment & Status
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cod')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')

    # Razorpay Gateway details
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=200, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Orders'

    def __str__(self):
        return f"Order #{self.order_number} ({self.full_name})"

    @classmethod
    def generate_order_number(cls):
        import random
        num = random.randint(10000, 99999)
        return f"BIT-ORD-{num}"

    def is_invoice_token_valid(self, token):
        """
        Validates if the provided token matches this order's invoice_access_token.
        Can be extended in the future for expiration or rotation logic.
        """
        if not token or not self.invoice_access_token:
            return False
        return str(self.invoice_access_token).lower() == str(token).lower()


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_items',
    )
    product_title = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product_title} in Order #{self.order.order_number}"



