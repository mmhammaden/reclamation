"""
Production settings for Reclamations ISCAE project.
"""
from .base import *

DEBUG = False

# Security settings
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Allowed hosts must be set in production
ALLOWED_HOSTS = env('DJANGO_ALLOWED_HOSTS').split(',')

# CORS - restrict in production
CORS_ALLOWED_ORIGINS = env('CORS_ALLOWED_ORIGINS').split(',')
CORS_ALLOW_ALL_ORIGINS = False

# Static files
STATIC_ROOT = '/var/www/static/'
MEDIA_ROOT = '/var/www/media/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Email backend - use SMTP in production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = True