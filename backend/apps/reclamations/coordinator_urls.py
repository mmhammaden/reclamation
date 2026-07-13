from django.urls import path
from . import coordinator_views

urlpatterns = [
    path('dashboard/', coordinator_views.DashboardView.as_view(), name='coordinator-dashboard'),
    path('reclamations/', coordinator_views.PendingReclamationListView.as_view(), name='coordinator-reclamations'),
    path('reclamations/<int:pk>/', coordinator_views.ReclamationDetailView.as_view(), name='coordinator-reclamation-detail'),
    path('reclamations/<int:pk>/traiter/', coordinator_views.traiter_reclamation, name='reclamation-traiter'),
    path('reclamations/<int:pk>/accepter/', coordinator_views.accepter_reclamation, name='reclamation-accepter'),
    path('reclamations/<int:pk>/rejeter/', coordinator_views.rejeter_reclamation, name='reclamation-rejeter'),
    path('reclamations/<int:pk>/envoyer-professeur/', coordinator_views.envoyer_professeur, name='reclamation-envoyer-professeur'),
    path('enseignants/', coordinator_views.list_enseignants, name='coordinator-enseignants'),
]
