from django.test import SimpleTestCase
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.views import exception_handler
from common.exceptions import custom_exception_handler


class CommonUtilitiesTests(SimpleTestCase):
    def test_custom_exception_handler_validation_error(self):
        exc = ValidationError({'email': ['This field is required.']})
        context = {}
        response = custom_exception_handler(exc, context)

        self.assertIsNotNone(response)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['message'], 'email: This field is required.')
        self.assertIn('email', response.data['errors'])

    def test_custom_exception_handler_permission_denied(self):
        exc = PermissionDenied('Access denied.')
        context = {}
        response = custom_exception_handler(exc, context)

        self.assertIsNotNone(response)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['message'], 'Access denied.')
