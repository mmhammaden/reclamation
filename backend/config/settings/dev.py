"""
Development settings for Reclamations ISCAE project.
"""
from .base import *

DEBUG = True

# Restrict CORS to specific origins even in dev for security
# Production should also define CORS_ALLOWED_ORIGINS in prod.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200",  # Angular dev server
    "http://localhost:3000",  # Alternative frontend port
    "http://127.0.0.1:4200",  # Alternative localhost format
]

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