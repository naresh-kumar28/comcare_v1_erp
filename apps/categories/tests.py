from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.categories.models import Category

User = get_user_model()


class CategoryAPITests(APITestCase):
    def setUp(self):
        self.category1 = Category.objects.create(name='Laptops', slug='laptops', is_active=True)
        self.category2 = Category.objects.create(name='Desktops', slug='desktops', is_active=True)
        self.category_inactive = Category.objects.create(name='Draft Category', slug='draft', is_active=False)

        self.list_url = reverse('category-list')
        self.detail_url = reverse('category-detail', kwargs={'slug': 'laptops'})

        self.admin_user = User.objects.create_superuser(email='admin@example.com', password='AdminPassword123!')
        self.normal_user = User.objects.create_user(email='user@example.com', password='UserPassword123!')

    def test_list_categories_public(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        # Public users should only see active categories (2 active)
        self.assertEqual(response.data['count'], 2)

    def test_retrieve_category_by_slug(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Laptops')

    def test_create_category_permission_denied_for_normal_user(self):
        self.client.force_authenticate(user=self.normal_user)
        payload = {'name': 'Monitors', 'slug': 'monitors'}
        response = self.client.post(self.list_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_category_allowed_for_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        payload = {'name': 'Monitors', 'slug': 'monitors'}
        response = self.client.post(self.list_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 4)
