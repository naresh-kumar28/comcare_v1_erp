import io
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from apps.categories.models import Category
from apps.store.models import Product, ProductGalleryImage


def make_image(name='test.jpg', size=(100, 100), color='blue'):
    file_obj = io.BytesIO()
    img = Image.new('RGB', size, color=color)
    img.save(file_obj, 'JPEG')
    file_obj.seek(0)
    return SimpleUploadedFile(name, file_obj.read(), content_type='image/jpeg')


class StoreAPITests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Laptops', slug='laptops', is_active=True)

        self.product1 = Product.objects.create(
            category=self.category,
            title='Dell XPS 13',
            slug='dell-xps-13',
            sku='DELL-XPS13-001',
            brand='Dell',
            selling_price=120000.00,
            original_price=135000.00,
            stock_qty=10,
            is_featured=True,
            is_active=True
        )

        self.product2 = Product.objects.create(
            category=self.category,
            title='MacBook Pro 14',
            slug='macbook-pro-14',
            sku='APPLE-MBP14-001',
            brand='Apple',
            selling_price=190000.00,
            original_price=200000.00,
            stock_qty=5,
            is_new_arrival=True,
            is_best_seller=True,
            is_active=True
        )

        ProductGalleryImage.objects.create(
            product=self.product1,
            image='store_products/gallery/sample.jpg',
            alt_text='Side View'
        )

        self.list_url = reverse('product-list')
        self.detail_url = reverse('product-detail', kwargs={'slug': 'dell-xps-13'})
        self.featured_url = reverse('product-featured')
        self.new_arrivals_url = reverse('product-new-arrivals')
        self.best_sellers_url = reverse('product-best-sellers')

    def test_list_products(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['count'], 2)

    def test_filter_products_by_brand(self):
        response = self.client.get(f"{self.list_url}?brand=Dell")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['brand'], 'Dell')

    def test_filter_products_by_price_range(self):
        response = self.client.get(f"{self.list_url}?min_price=150000")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'MacBook Pro 14')

    def test_retrieve_product_detail_by_slug(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Dell XPS 13')
        self.assertEqual(len(response.data['gallery_images']), 1)
        self.assertEqual(response.data['gallery_images'][0]['alt_text'], 'Side View')

    def test_featured_products_endpoint(self):
        response = self.client.get(self.featured_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Dell XPS 13')

    def test_new_arrivals_endpoint(self):
        response = self.client.get(self.new_arrivals_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_best_sellers_endpoint(self):
        response = self.client.get(self.best_sellers_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)