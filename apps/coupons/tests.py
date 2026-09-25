from decimal import Decimal

from django.test import TestCase

from apps.coupons.models import Coupon


class CouponModelTests(TestCase):
    def test_code_normalized_to_uppercase_on_save(self):
        coupon = Coupon.objects.create(code='  save10 ', discount_type='percentage', discount_value=Decimal('10.00'))
        self.assertEqual(coupon.code, 'SAVE10')

    def test_percentage_discount_capped(self):
        coupon = Coupon.objects.create(
            code='CAP20', discount_type='percentage', discount_value=Decimal('20.00'),
            max_discount_amount=Decimal('50.00'),
        )
        self.assertEqual(coupon.calculate_discount(Decimal('1000.00')), Decimal('50.00'))
        self.assertEqual(coupon.calculate_discount(Decimal('100.00')), Decimal('20.00'))

    def test_fixed_discount(self):
        coupon = Coupon.objects.create(code='FIX15', discount_type='fixed', discount_value=Decimal('15.00'))
        self.assertEqual(coupon.calculate_discount(Decimal('500.00')), Decimal('15.00'))

    def test_discount_never_exceeds_subtotal(self):
        coupon = Coupon.objects.create(code='BIG', discount_type='fixed', discount_value=Decimal('9999.00'))
        self.assertEqual(coupon.calculate_discount(Decimal('50.00')), Decimal('50.00'))

    def test_is_valid_active_and_usage_limit(self):
        coupon = Coupon.objects.create(
            code='LIMIT1', discount_type='fixed', discount_value=Decimal('10.00'),
            usage_limit=1, used_count=0,
        )
        self.assertTrue(coupon.is_valid(Decimal('100.00'))[0])

        coupon.used_count = 1
        coupon.save()
        self.assertFalse(coupon.is_valid(Decimal('100.00'))[0])

    def test_is_valid_requires_min_order(self):
        coupon = Coupon.objects.create(
            code='MIN500', discount_type='fixed', discount_value=Decimal('10.00'),
            min_order_amount=Decimal('500.00'),
        )
        is_valid, error = coupon.is_valid(Decimal('100.00'))
        self.assertFalse(is_valid)
        self.assertTrue(error)

    def test_is_valid_expired_coupon(self):
        from datetime import timedelta
        from django.utils import timezone
        coupon = Coupon.objects.create(
            code='EXPIRED', discount_type='fixed', discount_value=Decimal('10.00'),
            valid_to=timezone.now() - timedelta(days=1),
        )
        self.assertFalse(coupon.is_valid(Decimal('100.00'))[0])