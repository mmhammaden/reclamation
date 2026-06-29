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
    Filters by modules assigned to this teacher via User.modules_enseignes.
    """
    serializer_class = ReclamationListSerializer
    permission_classes = [permissions.IsAuthenticated, IsModuleTeacher]

    def get_queryset(self):
        user = self.request.user
        # Get the code_modules this teacher is assigned to
        assigned_codes = user.modules_enseignes.values_list('code_module', flat=True).distinct()
        return Reclamation.objects.filter(
            note_elementaire__code_module__in=assigned_codes
        ).select_related(
            'etudiant', 'note_elementaire'
        )
