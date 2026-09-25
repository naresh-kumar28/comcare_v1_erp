import tempfile

from django.test import TestCase, override_settings

from apps.categories.models import Category
from apps.store.models import Product
from apps.store.tests import make_image
from decimal import Decimal


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class HealthEndpointTests(TestCase):
    def test_health_returns_200(self):
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')

    def test_health_does_not_leak_information(self):
        response = self.client.get('/health/')
        body = response.content.decode()
        for secret_marker in ['secret', 'password', 'token', 'key', 'DATABASE_URL']:
            self.assertNotIn(secret_marker, body.lower())


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class PublicPageTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Laptops', slug='laptops', is_active=True)
        Product.objects.create(
            category=self.category,
            title='Test Laptop',
            slug='test-laptop',
            sku='SKU-CORE-1',
            selling_price=Decimal('1000.00'),
            image=make_image(),
            is_active=True,
        )

    def test_homepage_renders(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_static_pages_render(self):
        for url in ['/about/', '/contact/', '/privacy-policy/', '/terms/', '/refund-policy/', '/categories/']:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_url_resolution(self):
        from django.urls import reverse
        self.assertEqual(reverse('health'), '/health/')
        self.assertEqual(reverse('home'), '/')
        self.assertEqual(reverse('about'), '/about/')