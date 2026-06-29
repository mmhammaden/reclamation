"""
Development settings for Reclamations ISCAE project.
"""
from .base import *

DEBUG = True

# Allow all origins in dev
CORS_ALLOW_ALL_ORIGINS = True

# SQLite fallback for local dev without PostgreSQL
import sys
try:
    import psycopg2
except ImportError:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Dev-specific apps (optional, install with: pip install django-extensions)
# INSTALLED_APPS += [
#     'django_extensions',
# ]

# Show emails in console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'