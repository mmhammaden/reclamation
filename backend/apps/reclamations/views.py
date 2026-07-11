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
        # Build a proper Python dict instead of using QueryDict to ensure DRF handles many=True correctly
        import json
        lignes_raw = request.data.get('lignes', '[]')
        try:
            lignes = json.loads(lignes_raw) if isinstance(lignes_raw, str) else list(lignes_raw)
        except (ValueError, TypeError):
            lignes = []

        data = {
            'description': request.data.get('description', ''),
            'lignes': lignes,
        }
        serializer = ReclamationCreateSerializer(data=data, context={'request': request})
        if not serializer.is_valid():
            # Log validation errors for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Validation errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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
                'lignes__element_module', 'lignes__element_module__module'
            )
        return Reclamation.objects.none()


class ReclamationDetailView(generics.RetrieveAPIView):
    """
    GET /api/reclamations/{id}/
    Détail d'une réclamation avec historique et pièces jointes.
    """
    queryset = Reclamation.objects.prefetch_related(
        'pieces_jointes', 'historique_statuts__modifie_par', 'lignes__element_module', 'lignes__element_module__module'
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