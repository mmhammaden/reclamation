from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db import transaction
from .models import Reclamation, StatutReclamation, HistoriqueStatut
from .serializers import ReclamationListSerializer, ReclamationDetailSerializer
from .permissions import IsModuleTeacher
from apps.notifications.models import Notification
from django.db import models


class TeacherReclamationListView(generics.ListAPIView):
    serializer_class = ReclamationListSerializer
    permission_classes = [permissions.IsAuthenticated, IsModuleTeacher]

    def get_queryset(self):
        user = self.request.user
        # Affiche les réclamations directement assignées OU liées à ses modules via les lignes
        return Reclamation.objects.filter(
            models.Q(enseignant_assigne=user) | 
            models.Q(lignes__element_module__module__code_module__in=user.modules_enseignes.values_list('code_module', flat=True))
        ).distinct().prefetch_related('lignes__element_module', 'lignes__element_module__module').select_related('etudiant', 'coordonnateur')


class TeacherReclamationDetailView(generics.RetrieveAPIView):
    """
    GET /api/teacher/reclamations/{id}/
    Teacher: view detailed reclamation assigned to them.
    """
    serializer_class = ReclamationDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsModuleTeacher]
    
    def get_queryset(self):
        user = self.request.user
        # Only show reclamations assigned to this teacher or related to their modules
        return Reclamation.objects.filter(
            models.Q(enseignant_assigne=user) | 
            models.Q(lignes__element_module__module__code_module__in=user.modules_enseignes.values_list('code_module', flat=True))
        ).distinct().prefetch_related(
            'pieces_jointes', 
            'historique_statuts__modifie_par', 
            'lignes__element_module',
            'lignes__element_module__module',
            'lignes__pieces_jointes'
        ).select_related('etudiant', 'coordonnateur')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsModuleTeacher])
def renvoyer_coordinateur(request, pk):
    """
    POST /api/teacher/reclamations/{id}/renvoyer-coordinateur/
    Teacher: submit their review and send back to coordinator.
    Corps attendu : { "commentaire_professeur": "..." }
    """
    try:
        reclamation = Reclamation.objects.select_related('coordonnateur').get(
            pk=pk, 
            enseignant_assigne=request.user
        )
    except Reclamation.DoesNotExist:
        return Response(
            {"detail": "Réclamation introuvable ou non assignée à votre compte."}, 
            status=status.HTTP_404_NOT_FOUND
        )


    commentaire = request.data.get('commentaire_professeur')
    if not commentaire or not commentaire.strip():
        return Response(
            {"detail": "Le commentaire d'évaluation du professeur est obligatoire."}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    if reclamation.statut != StatutReclamation.EN_REVISION_ENSEIGNANT:
        return Response(
            {"detail": "Cette réclamation n'est pas en attente de votre révision."}, 
            status=status.HTTP_400_BAD_REQUEST
        )

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

    from .coordinator_views import _get_reclamation_for_response
    return Response(ReclamationDetailSerializer(_get_reclamation_for_response(reclamation.pk)).data)


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated, IsModuleTeacher])
def modifier_revision(request, pk):
    """
    PATCH /api/teacher/reclamations/{id}/modifier-revision/
    Teacher: update their review comment while still in EN_REVISION_ENSEIGNANT status.
    Corps attendu : { "commentaire_professeur": "..." }
    """
    try:
        reclamation = Reclamation.objects.get(pk=pk, enseignant_assigne=request.user)
    except Reclamation.DoesNotExist:
        return Response(
            {"detail": "Réclamation introuvable ou non assignée à votre compte."}, 
            status=status.HTTP_404_NOT_FOUND
        )

    # Can only edit while still under review
    if reclamation.statut != StatutReclamation.EN_REVISION_ENSEIGNANT:
        return Response(
            {"detail": "Vous ne pouvez modifier la révision que si la réclamation est en attente de votre révision."}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    commentaire = request.data.get('commentaire_professeur')
    if not commentaire or not commentaire.strip():
        return Response(
            {"detail": "Le commentaire d'évaluation du professeur est obligatoire."}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    reclamation.commentaire_professeur = commentaire
    reclamation.save()

    from .coordinator_views import _get_reclamation_for_response
    return Response(ReclamationDetailSerializer(_get_reclamation_for_response(reclamation.pk)).data)
