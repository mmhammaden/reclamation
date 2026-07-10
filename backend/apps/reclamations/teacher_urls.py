from django.urls import path
from . import teacher_views

urlpatterns = [
    path('reclamations/', teacher_views.TeacherReclamationListView.as_view(), name='teacher-reclamations'),
    path('reclamations/<int:pk>/renvoyer-coordinateur/', teacher_views.renvoyer_coordinateur, name='teacher-renvoyer-coordinateur'),
]