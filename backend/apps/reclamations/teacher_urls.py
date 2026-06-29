from django.urls import path
from . import teacher_views

urlpatterns = [
    path('reclamations/', teacher_views.TeacherReclamationListView.as_view(), name='teacher-reclamations'),
]