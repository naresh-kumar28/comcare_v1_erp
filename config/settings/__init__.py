"""
Settings package initialization.
Loads development or production settings dynamically based on DJANGO_ENV or DJANGO_DEBUG.
"""

import os
from decouple import config

env_name = config('DJANGO_ENV', default='development').lower()

if env_name == 'production' or os.environ.get('DJANGO_ENV') == 'production':
    from .production import *
else:
    from .development import *
