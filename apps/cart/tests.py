import json
import tempfile
import uuid
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase, override_settings

from apps.cart.models import (
    Cart,
    CartItem,
    Order,
    OrderItem,
    ShippingConfig,
    UserAddress,
)
from apps.categories.models import Category
from apps.store.models import Product
from apps.store.tests import make_image


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class OrderModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Laptops', slug='laptops', is_active=True)
        self.product = Product.objects.create(
            category=self.category,
            title='Test Laptop',
            slug='test-laptop',
            sku='SKU-CART-1',
            selling_price=Decimal('1000.00'),
            image=make_image(),
            is_active=True,
        )

    def create_order(self, **kwargs):
        fields = {
            'order_number': Order.generate_order_number(),
            'full_name': 'Test User',
            'phone': '9876543210',
            'email': 'test@example.com',
            'address_line1': 'Main Road',
            'city': 'Purnea',
            'state': 'Bihar',
            'pincode': '854301',
            'subtotal': Decimal('1000.00'),
            'tax': Decimal('180.00'),
            'grand_total': Decimal('1180.00'),
            'payment_method': 'cod',
            'payment_status': 'pending',
            'order_status': 'pending',
        }
        fields.update(kwargs)
        return Order.objects.create(**fields)

    def test_generate_order_number_format(self):
        order_number = Order.generate_order_number()
        self.assertRegex(order_number, r'^BIT-ORD-\d{5}$')

    def test_invoice_token_valid_case_insensitive(self):
        order = self.create_order()
        token = str(order.invoice_access_token)
        self.assertTrue(order.is_invoice_token_valid(token))
        self.assertTrue(order.is_invoice_token_valid(token.upper()))
        self.assertFalse(order.is_invoice_token_valid(str(uuid.uuid4())))
        self.assertFalse(order.is_invoice_token_valid(None))

    def test_shipping_config_is_singleton(self):
        cfg = ShippingConfig.get_config()
        cfg.flat_rate = Decimal('50.00')
        cfg.free_shipping_threshold = Decimal('500.00')
        cfg.save()

        again = ShippingConfig.get_config()
        self.assertEqual(again.pk, cfg.pk)
        self.assertEqual(ShippingConfig.objects.count(), 1)

        self.assertEqual(cfg.get_shipping_cost(Decimal('200.00')), Decimal('50.00'))
        self.assertEqual(cfg.get_shipping_cost(Decimal('600.00')), Decimal('0.00'))


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class CartViewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Laptops', slug='laptops', is_active=True)
        self.product = Product.objects.create(
            category=self.category,
            title='Test Laptop',
            slug='test-laptop',
            sku='SKU-CART-2',
            selling_price=Decimal('1000.00'),
            image=make_image(),
            is_active=True,
        )

    def test_add_cart_creates_cart_item_for_guest(self):
        response = self.client.get(f'/cart/add_cart/{self.product.id}/')
        self.assertEqual(response.status_code, 302)
        session_key = self.client.session.session_key
        self.assertIsNotNone(session_key)
        cart = Cart.objects.filter(session_key=session_key).first()
        self.assertIsNotNone(cart)
        item = CartItem.objects.filter(cart=cart, product=self.product).first()
        self.assertIsNotNone(item)
        self.assertGreaterEqual(item.quantity, 1)


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class CheckoutFlowTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Laptops', slug='laptops', is_active=True)
        self.product = Product.objects.create(
            category=self.category,
            title='Test Laptop',
            slug='test-laptop',
            sku='SKU-CART-3',
            selling_price=Decimal('1000.00'),
            image=make_image(),
            is_active=True,
        )

    def add_to_cart(self):
        self.client.get(f'/cart/add_cart/{self.product.id}/')

    def place_cod_order(self):
        self.add_to_cart()
        return self.client.post('/cart/place-order/', {
            'payment_method': 'cod',
            'full_name': 'Test User',
            'phone': '9876543210',
            'address_line1': 'Main Road',
            'pincode': '854301',
            'city': 'Purnea',
            'state': 'Bihar',
            'email': 'test@example.com',
        })

    def test_place_order_creates_order_with_server_side_pricing(self):
        response = self.place_cod_order()
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')

        order = Order.objects.get(order_number=data['redirect_url'].split('=')[1])
        self.assertEqual(order.payment_method, 'cod')
        self.assertEqual(order.subtotal, Decimal('1000.00'))
        self.assertEqual(order.tax, Decimal('180.00'))
        self.assertEqual(order.grand_total, Decimal('1180.00'))
        self.assertEqual(order.items.count(), 1)
        item = order.items.first()
        self.assertEqual(item.product_title, self.product.title)
        self.assertEqual(item.unit_price, Decimal('1000.00'))

    def test_order_success_visible_to_same_session(self):
        response = self.place_cod_order()
        order = Order.objects.latest('id')

        page = self.client.get(f'/cart/order-success/?order_number={order.order_number}')
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, order.order_number)

    def test_order_success_hidden_from_different_session(self):
        response = self.place_cod_order()
        order = Order.objects.latest('id')

        other_client = self.client.__class__()
        other_client.cookies = {}
        page = other_client.get(f'/cart/order-success/?order_number={order.order_number}')
        self.assertEqual(page.status_code, 200)
        self.assertNotContains(page, order.order_number)


@override_settings(
    MEDIA_ROOT=tempfile.mkdtemp(),
    DEBUG=False,
    RAZORPAY_KEY_ID='',
    RAZORPAY_KEY_SECRET='',
)
class PaymentVerificationSecurityTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Laptops', slug='laptops', is_active=True)
        self.product = Product.objects.create(
            category=self.category,
            title='Test Laptop',
            slug='test-laptop',
            sku='SKU-CART-4',
            selling_price=Decimal('1000.00'),
            image=make_image(),
            is_active=True,
        )
        self.order = Order.objects.create(
            order_number=Order.generate_order_number(),
            full_name='Test User',
            phone='9876543210',
            email='test@example.com',
            address_line1='Main Road',
            city='Purnea',
            state='Bihar',
            pincode='854301',
            subtotal=Decimal('1000.00'),
            tax=Decimal('180.00'),
            grand_total=Decimal('1180.00'),
            payment_method='razorpay',
            payment_status='pending',
            razorpay_order_id='rp_SERVER_CREATED_1',
        )

    def post_verify(self, order_number, rp_order_id):
        return self.client.post(
            '/cart/verify-payment/',
            data=json.dumps({
                'order_number': order_number,
                'razorpay_order_id': rp_order_id,
                'razorpay_payment_id': 'pay_123',
                'razorpay_signature': 'sig_123',
            }),
            content_type='application/json',
        )

    def test_production_without_keys_rejects_all_verification(self):
        response = self.post_verify(self.order.order_number, 'rp_SERVER_CREATED_1')
        self.assertEqual(response.status_code, 400)
        self.order.refresh_from_db()
        # The dangerous old sandbox auto-verify must NOT apply in production.
        self.assertEqual(self.order.payment_status, 'failed')

    def test_rejects_order_id_not_created_by_server(self):
        response = self.post_verify(self.order.order_number, 'rp_ATTACKER_OWNED_1')
        self.assertEqual(response.status_code, 400)
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'failed')

    @override_settings(RAZORPAY_KEY_ID='test_key', RAZORPAY_KEY_SECRET='test_secret')
    @patch('razorpay.Client')
    def test_valid_signature_with_matching_order_id_marks_paid(self, mock_client):
        response = self.post_verify(self.order.order_number, 'rp_SERVER_CREATED_1')
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'paid')
        self.assertEqual(self.order.order_status, 'processing')

    @override_settings(RAZORPAY_KEY_ID='test_key', RAZORPAY_KEY_SECRET='test_secret')
    @patch('razorpay.Client')
    def test_valid_signature_but_wrong_order_id_still_rejected(self, mock_client):
        # Even a cryptographically valid signature for a different order must fail.
        response = self.post_verify(self.order.order_number, 'rp_OTHER_ORDER')
        self.assertEqual(response.status_code, 400)
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'failed')

    @override_settings(RAZORPAY_KEY_ID='test_key', RAZORPAY_KEY_SECRET='test_secret')
    def test_already_paid_order_is_idempotent(self):
        self.order.payment_status = 'paid'
        self.order.order_status = 'processing'
        self.order.save()

        response = self.post_verify(self.order.order_number, 'whatever')
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'paid')