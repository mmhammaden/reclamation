"""
URL configuration for Reclamations ISCAE project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # API endpoints (will be added in Phase 3)
    path('api/auth/', include('apps.users.urls')),
    path('api/notes/', include('apps.notes.urls')),
    path('api/reclamations/', include('apps.reclamations.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/coordinator/', include('apps.reclamations.coordinator_urls')),
    path('api/admin/', include('apps.reclamations.admin_urls')),
    path('api/teacher/', include('apps.reclamations.teacher_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)