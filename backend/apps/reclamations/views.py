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
    Validates RG-02 (unicité) and RG-03 (conflit) business rules.
    """
    serializer_class = ReclamationCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsEtudiant]

    def create(self, request, *args, **kwargs):
        # Support multipart: lignes envoyées comme JSON string
        data = request.data.copy()
        if isinstance(data.get('lignes'), str):
            import json
            try:
                data['lignes'] = json.loads(data['lignes'])
            except (ValueError, TypeError):
                pass
        serializer = ReclamationCreateSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        reclamation = serializer.save()
        return Response(
            ReclamationDetailSerializer(reclamation).data,
            status=status.HTTP_201_CREATED
        )


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
            return Reclamation.objects.filter(etudiant=user).prefetch_related(
                'lignes__note_elementaire'
            )
        return Reclamation.objects.none()


class ReclamationDetailView(generics.RetrieveAPIView):
    """
    GET /api/reclamations/{id}/
    Détail d'une réclamation avec historique et pièces jointes.
    """
    queryset = Reclamation.objects.prefetch_related(
        'pieces_jointes', 'historique_statuts__modifie_par', 'lignes__note_elementaire'
    ).select_related('etudiant', 'coordonnateur')
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