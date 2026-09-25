from decimal import Decimal
from unittest.mock import patch
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.categories.models import Category
from apps.store.models import Product
from apps.cart.models import Order, OrderItem
from apps.payments.razorpay_client import RazorpayClientHelper

User = get_user_model()


class RazorpayAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='payer@example.com', password='Password123!')
        self.category = Category.objects.create(name='Laptops', slug='laptops', is_active=True)
        self.product = Product.objects.create(
            category=self.category,
            title='Test Laptop',
            slug='test-laptop',
            sku='SKU-PAY-01',
            brand='Dell',
            selling_price=50000.00,
            stock_qty=5
        )

        self.order = Order.objects.create(
            order_number='BIT-ORD-99999',
            user=self.user,
            full_name='Payer User',
            phone='9998887776',
            email='payer@example.com',
            address_line1='Main Street 123',
            city='Purnea',
            state='Bihar',
            pincode='854301',
            subtotal=Decimal('50000.00'),
            tax=Decimal('9000.00'),
            shipping_cost=Decimal('0.00'),
            grand_total=Decimal('59000.00'),
            payment_method='razorpay',
            payment_status='pending',
            order_status='pending'
        )

        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            product_title=self.product.title,
            quantity=1,
            unit_price=Decimal('50000.00'),
            total_price=Decimal('50000.00')
        )

        self.create_order_url = reverse('api_razorpay_create_order')
        self.verify_url = reverse('api_razorpay_verify')
        self.webhook_url = reverse('api_razorpay_webhook')

    def test_create_razorpay_order_success(self):
        self.client.force_authenticate(user=self.user)
        payload = {'order_number': 'BIT-ORD-99999'}
        response = self.client.post(self.create_order_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('razorpay_order_id', response.data)

        self.order.refresh_from_db()
        self.assertIsNotNone(self.order.razorpay_order_id)

    @patch.object(RazorpayClientHelper, 'verify_payment_signature', return_value=True)
    def test_verify_razorpay_payment_success(self, mock_verify):
        self.client.force_authenticate(user=self.user)
        self.order.razorpay_order_id = 'order_mock_12345'
        self.order.save()

        payload = {
            'order_number': 'BIT-ORD-99999',
            'razorpay_order_id': 'order_mock_12345',
            'razorpay_payment_id': 'pay_mock_67890',
            'razorpay_signature': 'mock_signature'
        }
        response = self.client.post(self.verify_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'paid')
        self.assertEqual(self.order.order_status, 'processing')

    @patch.object(RazorpayClientHelper, 'verify_webhook_signature', return_value=True)
    def test_razorpay_webhook_signature_and_event(self, mock_wh_verify):
        self.order.razorpay_order_id = 'order_webhook_123'
        self.order.save()

        webhook_payload = {
            'event': 'order.paid',
            'payload': {
                'payment': {
                    'entity': {
                        'id': 'pay_wh_123',
                        'order_id': 'order_webhook_123',
                        'notes': {
                            'order_number': 'BIT-ORD-99999'
                        }
                    }
                }
            }
        }
        response = self.client.post(
            self.webhook_url,
            data=webhook_payload,
            format='json',
            HTTP_X_RAZORPAY_SIGNATURE='dummy_sig'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'paid')
