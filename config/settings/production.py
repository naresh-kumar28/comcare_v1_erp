"""
Production settings for ComCare ERP.
"""

from .base import *
from django.core.exceptions import ImproperlyConfigured

DEBUG = False

SESSION_COOKIE_SECURE = config('DJANGO_SESSION_COOKIE_SECURE', default=True, cast=bool)
CSRF_COOKIE_SECURE = config('DJANGO_CSRF_COOKIE_SECURE', default=True, cast=bool)
SECURE_SSL_REDIRECT = config('DJANGO_SECURE_SSL_REDIRECT', default=False, cast=bool)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SECURE_HSTS_SECONDS = config('DJANGO_HSTS_SECONDS', default=31536000, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = config('DJANGO_HSTS_PRELOAD', default=False, cast=bool)

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = config('DJANGO_SECURE_REFERRER_POLICY', default='strict-origin-when-cross-origin')
X_FRAME_OPTIONS = 'DENY'

STORAGES["staticfiles"]["BACKEND"] = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Cloudinary verification in production if credentials supplied
_is_cloudinary_configured = all([
    config('CLOUDINARY_CLOUD_NAME', default=''),
    config('CLOUDINARY_API_KEY', default=''),
    config('CLOUDINARY_API_SECRET', default=''),
])

if _is_cloudinary_configured:
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME'),
        'API_KEY': config('CLOUDINARY_API_KEY'),
        'API_SECRET': config('CLOUDINARY_API_SECRET'),
    }
    STORAGES["default"]["BACKEND"] = "cloudinary_storage.storage.MediaCloudinaryStorage"

# Validate DB in production
if not _database_url and not DATABASES.get('default', {}).get('ENGINE', '').endswith('sqlite3'):
    raise ImproperlyConfigured('DATABASE_URL is required in production.')
