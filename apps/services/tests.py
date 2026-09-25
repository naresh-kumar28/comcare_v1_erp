from django.test import TestCase

from apps.services.models import Service


class ServiceModelTests(TestCase):
    def test_slug_auto_generated_from_title(self):
        service = Service.objects.create(title='Laptop Repair')
        service.refresh_from_db()
        self.assertEqual(service.slug, 'laptop-repair')

    def test_slug_preserved_when_set(self):
        service = Service.objects.create(title='Phone Repair', slug='custom-slug')
        service.refresh_from_db()
        self.assertEqual(service.slug, 'custom-slug')