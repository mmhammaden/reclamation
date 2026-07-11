from rest_framework import generics, permissions
from .models import ResultatSemestre
from .serializers import ResultatSemestreSerializer


class NoteListView(generics.ListAPIView):
    """
    GET /api/notes/
    Étudiant: voir ses propres résultats de semestre avec modules et éléments.
    Coordinateur/Admin: voir tous les résultats.
    """
    serializer_class = ResultatSemestreSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_etudiant():
            return ResultatSemestre.objects.filter(
                etudiant=user
            ).prefetch_related(
                'modules__elements'
            )
        return ResultatSemestre.objects.prefetch_related(
            'modules__elements'
        )


class NoteDetailView(generics.RetrieveAPIView):
    """
    GET /api/notes/{id}/
    Détail d'un résultat de semestre avec modules et éléments.
    """
    queryset = ResultatSemestre.objects.prefetch_related('modules__elements')
    serializer_class = ResultatSemestreSerializer
    permission_classes = [permissions.IsAuthenticated]