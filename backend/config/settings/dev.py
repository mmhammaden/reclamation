"""
Development settings for Reclamations ISCAE project.
"""
from .base import *

DEBUG = True

# Allow all hosts in development for mobile testing
ALLOWED_HOSTS = ['*']

# CORS - use environment variable or allow all in development
CORS_ALLOW_ALL_ORIGINS = True  # Allow all origins in dev for simplicity

# Use SQLite for local development
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