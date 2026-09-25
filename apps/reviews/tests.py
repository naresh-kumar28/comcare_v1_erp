import tempfile
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase, override_settings

from apps.categories.models import Category
from apps.store.models import Product
from apps.store.tests import make_image
from apps.reviews.models import Review


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ReviewRatingClampTests(TestCase):
    def setUp(self):
        self.user = self._create_user()
        self.category = Category.objects.create(name='Laptops', slug='laptops', is_active=True)
        self.product = Product.objects.create(
            category=self.category,
            title='Test Laptop',
            slug='test-laptop',
            sku='SKU-REV-1',
            selling_price=Decimal('1000.00'),
            image=make_image(),
            is_active=True,
        )
        self.client.force_login(self.user)

    @staticmethod
    def _create_user():
        from apps.accounts.models import CustomUser
        return CustomUser.objects.create_user(
            email='reviewer@example.com', password='testpass123'
        )

    @patch('apps.reviews.views.check_verified_purchase', return_value=True)
    def test_out_of_range_rating_is_clamped(self, _mock):
        response = self.client.post(f'/reviews/submit/{self.product.id}/', {
            'rating': '99',
            'title': 'Great',
            'comment': 'Works well',
        })
        self.assertEqual(response.status_code, 200)
        review = Review.objects.get(user=self.user, product=self.product)
        self.assertLessEqual(review.rating, 5)

    @patch('apps.reviews.views.check_verified_purchase', return_value=True)
    def test_negative_rating_is_clamped(self, _mock):
        response = self.client.post(f'/reviews/submit/{self.product.id}/', {
            'rating': '-5',
            'title': 'Poor',
            'comment': 'Bad',
        })
        self.assertEqual(response.status_code, 200)
        review = Review.objects.get(user=self.user, product=self.product)
        self.assertGreaterEqual(review.rating, 1)

    @patch('apps.reviews.views.check_verified_purchase', return_value=True)
    def test_review_updates_product_rating(self, _mock):
        self.client.post(f'/reviews/submit/{self.product.id}/', {
            'rating': '4',
            'title': 'Nice',
            'comment': 'OK',
        })
        self.product.refresh_from_db()
        self.assertEqual(self.product.rating, Decimal('4.0'))
        self.assertEqual(self.product.reviews_count, 1)