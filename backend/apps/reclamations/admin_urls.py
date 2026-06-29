from django.urls import path
from . import admin_views

urlpatterns = [
    path('import-pv/', admin_views.import_pv, name='admin-import-pv'),
    path('rapports/', admin_views.export_rapport, name='admin-rapports'),
    path('reclamations/<int:reclamation_id>/force-unblock/', admin_views.force_unblock_note, name='admin-force-unblock'),
]
