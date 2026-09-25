from decimal import Decimal

from django.db import models
from django.utils import timezone


class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('fixed', 'Fixed Amount (₹)'),
        ('percentage', 'Percentage (%)'),
    ]

    code = models.CharField(
        max_length=50,
        unique=True,
        help_text='Unique coupon code (stored & matched in uppercase).',
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        help_text='Short description shown to admin (e.g. "Welcome offer ₹500 off").',
    )
    discount_type = models.CharField(
        max_length=10,
        choices=DISCOUNT_TYPE_CHOICES,
        default='fixed',
    )
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Discount value — flat ₹ amount or percentage.',
    )
    min_order_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Minimum cart subtotal required to use this coupon.',
    )
    max_discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Cap on max discount for percentage coupons (leave blank for no cap).',
    )
    usage_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Max number of times this coupon can be used (blank = unlimited).',
    )
    used_count = models.PositiveIntegerField(default=0)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Coupon expiry date/time (blank = never expires).',
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Coupon'
        verbose_name_plural = 'Coupons'

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        self.code = self.code.upper().strip()
        super().save(*args, **kwargs)

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------

    def is_valid(self, subtotal=Decimal('0.00')):
        """Return (bool, error_message) tuple."""
        now = timezone.now()

        if not self.is_active:
            return False, 'This coupon is no longer active.'

        if self.valid_from and now < self.valid_from:
            return False, 'This coupon is not yet valid.'

        if self.valid_to and now > self.valid_to:
            return False, 'This coupon has expired.'

        if self.usage_limit is not None and self.used_count >= self.usage_limit:
            return False, 'This coupon has reached its usage limit.'

        if subtotal < self.min_order_amount:
            return False, f'Minimum order of ₹{self.min_order_amount:.0f} required for this coupon.'

        return True, ''

    def calculate_discount(self, subtotal):
        """Return the actual discount amount for the given subtotal."""
        if self.discount_type == 'percentage':
            discount = (self.discount_value / Decimal('100')) * subtotal
            if self.max_discount_amount is not None:
                discount = min(discount, self.max_discount_amount)
        else:
            discount = self.discount_value

        # Never discount more than the subtotal
        return min(discount, subtotal)
