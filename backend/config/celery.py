"""
Celery app configuration for Reclamations ISCAE.
"""
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

app = Celery('reclamations')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()