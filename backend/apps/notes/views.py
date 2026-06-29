from rest_framework import generics, permissions
from .models import NoteElementaire
from .serializers import NoteElementaireSerializer


class NoteListView(generics.ListAPIView):
    """
    GET /api/notes/
    Étudiant: voir ses propres notes.
    Coordinateur/Admin: voir toutes les notes.
    """
    serializer_class = NoteElementaireSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_etudiant():
            return NoteElementaire.objects.filter(etudiant=user)
        return NoteElementaire.objects.select_related('etudiant').all()


class NoteDetailView(generics.RetrieveAPIView):
    """
    GET /api/notes/{id}/
    Détail d'une note.
    """
    queryset = NoteElementaire.objects.all()
    serializer_class = NoteElementaireSerializer
    permission_classes = [permissions.IsAuthenticated]