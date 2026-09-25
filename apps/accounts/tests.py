from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthAPITests(APITestCase):
    def setUp(self):
        self.register_url = reverse('api_auth_register')
        self.login_url = reverse('api_auth_login')
        self.refresh_url = reverse('api_auth_refresh')
        self.logout_url = reverse('api_auth_logout')
        self.me_url = reverse('api_auth_me')
        self.change_password_url = reverse('api_auth_password_change')

        self.user_data = {
            'email': 'testuser@example.com',
            'password': 'StrongPassword123!',
            'password_confirm': 'StrongPassword123!',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '9876543210'
        }
        self.user = User.objects.create_user(
            email='existing@example.com',
            password='StrongPassword123!',
            first_name='Existing',
            last_name='User'
        )

    def test_user_registration_success(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])

    def test_user_login_success(self):
        login_data = {
            'email': 'existing@example.com',
            'password': 'StrongPassword123!'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('access', response.data['tokens'])

    def test_user_profile_me_endpoint(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)

        # Test profile update (PATCH)
        patch_data = {'first_name': 'UpdatedFirst'}
        patch_response = self.client.patch(self.me_url, patch_data, format='json')
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.data['first_name'], 'UpdatedFirst')

    def test_password_change_success(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            'old_password': 'StrongPassword123!',
            'new_password': 'BrandNewPassword123!',
            'new_password_confirm': 'BrandNewPassword123!'
        }
        response = self.client.post(self.change_password_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

    def test_logout_blacklists_token(self):
        login_data = {'email': 'existing@example.com', 'password': 'StrongPassword123!'}
        login_resp = self.client.post(self.login_url, login_data, format='json')
        refresh_token = login_resp.data['tokens']['refresh']
        access_token = login_resp.data['tokens']['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        logout_resp = self.client.post(self.logout_url, {'refresh': refresh_token}, format='json')
        self.assertEqual(logout_resp.status_code, status.HTTP_200_OK)

        # Attempt to refresh token after logout should fail
        refresh_resp = self.client.post(self.refresh_url, {'refresh': refresh_token}, format='json')
        self.assertEqual(refresh_resp.status_code, status.HTTP_401_UNAUTHORIZED)
