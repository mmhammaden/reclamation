from django.urls import path
from . import teacher_views

urlpatterns = [
    path('reclamations/', teacher_views.TeacherReclamationListView.as_view(), name='teacher-reclamations'),
    path('reclamations/', teacher_views.TeacherReclamationListView.as_view(), name='teacher-reclamations-list'),
    path('reclamations/<int:pk>/', teacher_views.TeacherReclamationDetailView.as_view(), name='teacher-reclamations-detail'),
    path('reclamations/<int:pk>/envoyer-revision/', teacher_views.modifier_revision, name='teacher-send-review'),
    path('reclamations/<int:pk>/modifier-revision/', teacher_views.modifier_revision, name='teacher-update-review'),
    path('reclamations/<int:pk>/renvoyer-coordinateur/', teacher_views.renvoyer_coordinateur, name='teacher-renvoyer-coordinateur'),

]

