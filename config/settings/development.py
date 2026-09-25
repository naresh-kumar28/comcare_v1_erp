"""
Development settings for ComCare ERP.
"""

from .base import *

DEBUG = True

# In dev, allow all local origins if needed
CORS_ALLOW_ALL_ORIGINS = config('CORS_ALLOW_ALL_ORIGINS', default=False, cast=bool)

# Console email backend in dev if non-explicit
if not config('EMAIL_HOST_USER', default=''):
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
