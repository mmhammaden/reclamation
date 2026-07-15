from django.urls import path, include
from . import admin_views

urlpatterns = [
    path('import-pv/', admin_views.import_pv, name='admin-import-pv'),
    path('rapports/', admin_views.export_rapport, name='admin-rapports'),
    path('reclamations/<int:reclamation_id>/force-unblock/', admin_views.force_unblock_note, name='admin-force-unblock'),
    path('annee-academique/current/', admin_views.annee_academique_current, name='admin-annee-current'),
    path('annee-academique/', admin_views.annee_academique_create, name='admin-annee-create'),
    path('annee-academique/<int:pk>/', admin_views.annee_academique_update, name='admin-annee-update'),
    path('users/', include('apps.users.admin_urls')),
]