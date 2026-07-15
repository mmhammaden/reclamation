from rest_framework import generics, permissions
from .models import ResultatSemestre
from .serializers import ResultatSemestreSerializer


class NoteListView(generics.ListAPIView):
    """
    GET /api/notes/
    Étudiant: voir ses propres résultats de semestre.
    Coordinateur/Admin: voir tous les résultats.
    """
    serializer_class = ResultatSemestreSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = ResultatSemestre.objects.prefetch_related('elements')
        if self.request.user.is_etudiant():
            qs = qs.filter(etudiant=self.request.user)
        # Filter by annee_academique if query param provided
        annee = self.request.query_params.get('annee_academique')
        if annee:
            qs = qs.filter(annee_academique=annee)
        return qs


class NoteDetailView(generics.RetrieveAPIView):
    """
    GET /api/notes/{id}/
    Détail d'un résultat de semestre avec éléments.
    """
    queryset = ResultatSemestre.objects.prefetch_related('elements')
    serializer_class = ResultatSemestreSerializer
    permission_classes = [permissions.IsAuthenticated]
