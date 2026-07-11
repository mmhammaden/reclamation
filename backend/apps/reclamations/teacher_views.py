from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db import transaction
from django.db import models
from .models import Reclamation, StatutReclamation, HistoriqueStatut
from .serializers import ReclamationListSerializer, ReclamationDetailSerializer
from .permissions import IsModuleTeacher
from apps.notifications.models import Notification

class TeacherReclamationListView(generics.ListAPIView):
    serializer_class = ReclamationListSerializer
    permission_classes = [permissions.IsAuthenticated, IsModuleTeacher]

    def get_queryset(self):
        user = self.request.user
        # Affiche les réclamations directement assignées OU liées à ses modules via les lignes
        return Reclamation.objects.filter(
            models.Q(enseignant_assigne=user) | 
            models.Q(lignes__element_module__module__code_module__in=user.modules_enseignes.values_list('code_module', flat=True))
        ).distinct().prefetch_related('lignes__element_module', 'lignes__element_module__module')

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsModuleTeacher])
def renvoyer_coordinateur(request, pk):
    """
    POST /api/teacher/reclamations/{id}/renvoyer-coordinateur/
    Corps attendu : { "commentaire_professeur": "..." }
    """
    try:
        reclamation = Reclamation.objects.get(pk=pk, enseignant_assigne=request.user)
    except Reclamation.DoesNotExist:
        return Response({"detail": "Réclamation introuvable ou non assignée à votre compte."}, status=status.HTTP_404_NOT_FOUND)

    commentaire = request.data.get('commentaire_professeur')
    if not commentaire or not commentaire.strip():
        return Response({"detail": "Le commentaire d'évaluation du professeur est obligatoire."}, status=status.HTTP_400_BAD_REQUEST)

    if reclamation.statut != StatutReclamation.EN_REVISION_ENSEIGNANT:
        return Response({"detail": "Cette réclamation n'est pas en attente de votre révision."}, status=status.HTTP_400_BAD_REQUEST)

    ancien_statut = reclamation.statut
    with transaction.atomic():
        reclamation.statut = StatutReclamation.EN_COURS
        reclamation.commentaire_professeur = commentaire
        reclamation.save()

        HistoriqueStatut.objects.create(
            reclamation=reclamation,
            statut_precedent=ancien_statut,
            nouveau_statut=StatutReclamation.EN_COURS,
            modifie_par=request.user,
            commentaire=f"Avis rendu par le professeur. Commentaire : {commentaire}",
        )
        
        if reclamation.coordonnateur:
            Notification.objects.create(
                destinataire=reclamation.coordonnateur,
                reclamation=reclamation,
                contenu=f"Le professeur a validé sa révision sur le dossier #{reclamation.id}.",
                type_notification='INFORMATION',
            )

    return Response(ReclamationDetailSerializer(reclamation).data)