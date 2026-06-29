"""
Teacher views - read-only access to reclamations for their modules.
"""
from rest_framework import generics, permissions
from .models import Reclamation
from .serializers import ReclamationListSerializer
from .permissions import IsModuleTeacher


class TeacherReclamationListView(generics.ListAPIView):
    """
    GET /api/teacher/reclamations/
    Enseignant: list reclamations for their modules (read-only).
    """
    serializer_class = ReclamationListSerializer
    permission_classes = [permissions.IsAuthenticated, IsModuleTeacher]

    def get_queryset(self):
        # TODO: Filter by modules assigned to this teacher
        # For now, return all reclamations with note_elementaire data
        return Reclamation.objects.select_related(
            'etudiant', 'note_elementaire'
        ).all()