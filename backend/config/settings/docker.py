"""
Docker settings for Reclamations ISCAE project.
Uses PostgreSQL for Docker deployment with development-friendly settings.
"""
from .base import *

DEBUG = True

# Allow all hosts in Docker for flexibility
ALLOWED_HOSTS = ['*']

# CORS - allow all origins in Docker for mobile testing
CORS_ALLOW_ALL_ORIGINS = True

# Use PostgreSQL in Docker
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default='reclamations_db'),
        'USER': env('DB_USER', default='reclamations_user'),
        'PASSWORD': env('DB_PASSWORD', default=''),
        'HOST': env('DB_HOST', default='postgres'),
        'PORT': env('DB_PORT', default='5432'),
        'CONN_MAX_AGE': 60,
    }
}

# Static files
STATIC_ROOT = '/app/staticfiles/'
MEDIA_ROOT = '/app/media/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Email backend - console for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'