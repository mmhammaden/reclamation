"""
Student-facing views for reclamations.
"""
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.utils import timezone
from .models import Reclamation, StatutReclamation
from .serializers import (
    ReclamationListSerializer,
    ReclamationDetailSerializer,
    ReclamationCreateSerializer,
)
from .permissions import IsOwnerOrCoordinator, IsEtudiant


class ReclamationCreateView(generics.CreateAPIView):
    """
    POST /api/reclamations/
    Étudiant: soumettre une nouvelle réclamation.
    Validates RG-02 (unicité) and RG-03 (conflit).
    """
    serializer_class = ReclamationCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsEtudiant]

    def perform_create(self, serializer):
        serializer.save(etudiant=self.request.user)


class ReclamationListView(generics.ListAPIView):
    """
    GET /api/reclamations/
    Étudiant: voir ses propres réclamations.
    """
    serializer_class = ReclamationListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_etudiant():
            return Reclamation.objects.filter(etudiant=user).select_related(
                'etudiant', 'note_elementaire'
            )
        return Reclamation.objects.none()


class ReclamationDetailView(generics.RetrieveAPIView):
    """
    GET /api/reclamations/{id}/
    Détail d'une réclamation avec historique et pièces jointes.
    """
    queryset = Reclamation.objects.prefetch_related(
        'pieces_jointes', 'historique_statuts__modifie_par'
    ).select_related('etudiant', 'note_elementaire', 'coordonnateur')
    serializer_class = ReclamationDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrCoordinator]


class ReclamationDeleteView(generics.DestroyAPIView):
    """
    DELETE /api/reclamations/{id}/
    Étudiant: annuler une réclamation si EN_ATTENTE.
    """
    queryset = Reclamation.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrCoordinator]

    def destroy(self, request, *args, **kwargs):
        reclamation = self.get_object()
        if not reclamation.peut_etre_modifiee():
            return Response(
                {"detail": "Seules les réclamations en attente peuvent être annulées."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)