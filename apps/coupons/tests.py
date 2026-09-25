from decimal import Decimal
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from apps.coupons.models import Coupon


class CouponAPITests(APITestCase):
    def setUp(self):
        self.coupon_fixed = Coupon.objects.create(
            code='WELCOME500',
            discount_type='fixed',
            discount_value=Decimal('500.00'),
            min_order_amount=Decimal('1000.00'),
            is_active=True
        )

        self.coupon_pct = Coupon.objects.create(
            code='SAVE10',
            discount_type='percentage',
            discount_value=Decimal('10.00'),
            max_discount_amount=Decimal('1000.00'),
            min_order_amount=Decimal('2000.00'),
            is_active=True
        )

        self.apply_url = reverse('api_coupon_apply')
        self.remove_url = reverse('api_coupon_remove')

    def test_apply_valid_fixed_coupon(self):
        payload = {'code': 'WELCOME500', 'cart_subtotal': '1500.00'}
        response = self.client.post(self.apply_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(Decimal(str(response.data['discount_amount'])), Decimal('500.00'))

    def test_apply_coupon_min_order_failed(self):
        payload = {'code': 'WELCOME500', 'cart_subtotal': '800.00'}
        response = self.client.post(self.apply_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])

    def test_remove_coupon(self):
        response = self.client.post(self.remove_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])