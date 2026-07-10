"""
Coordinator views for managing reclamations.
"""
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from django.db.models import Count, Q
from .models import Reclamation, StatutReclamation, HistoriqueStatut
from .serializers import (
    ReclamationListSerializer,
    ReclamationDetailSerializer,
    ReclamationDecisionSerializer,
)
from .permissions import IsCoordinator
from apps.audit.models import AuditLog
from apps.notifications.models import Notification


class DashboardView(generics.GenericAPIView):
    """
    GET /api/coordinator/dashboard/
    Returns counts by status and overdue count (RG-01).
    """
    permission_classes = [permissions.IsAuthenticated, IsCoordinator]

    def get(self, request, *args, **kwargs):
        now = timezone.now()
        stats = Reclamation.objects.aggregate(
            en_attente=Count('id', filter=Q(statut=StatutReclamation.EN_ATTENTE)),
            en_cours=Count('id', filter=Q(statut=StatutReclamation.EN_COURS)),
            acceptee=Count('id', filter=Q(statut=StatutReclamation.ACCEPTEE)),
            rejetee=Count('id', filter=Q(statut=StatutReclamation.REJETEE)),
            en_retard=Count('id', filter=Q(
                statut__in=[StatutReclamation.EN_ATTENTE, StatutReclamation.EN_COURS],
                date_limite_traitement__lt=now
            )),
        )
        return Response(stats)


class PendingReclamationListView(generics.ListAPIView):
    """
    GET /api/reclamations/pending/
    Coordinator: list all reclamations.
    """
    serializer_class = ReclamationListSerializer
    permission_classes = [permissions.IsAuthenticated, IsCoordinator]

    def get_queryset(self):
        return Reclamation.objects.select_related(
            'etudiant', 'note_elementaire'
        ).all()


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated, IsCoordinator])
def traiter_reclamation(request, pk):
    """
    PATCH /api/reclamations/{id}/traiter/
    Coordinator: mark as EN_COURS.
    """
    try:
        reclamation = Reclamation.objects.get(pk=pk)
    except Reclamation.DoesNotExist:
        return Response({"detail": "Réclamation introuvable."}, status=status.HTTP_404_NOT_FOUND)

    if reclamation.statut != StatutReclamation.EN_ATTENTE:
        return Response(
            {"detail": "Seules les réclamations en attente peuvent être traitées."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    ancien_statut = reclamation.statut
    reclamation.statut = StatutReclamation.EN_COURS
    reclamation.coordonnateur = request.user
    reclamation.save()

    HistoriqueStatut.objects.create(
        reclamation=reclamation,
        statut_precedent=ancien_statut,
        nouveau_statut=StatutReclamation.EN_COURS,
        modifie_par=request.user,
        commentaire="Prise en charge par le coordinateur",
    )

    serializer = ReclamationDetailSerializer(reclamation)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsCoordinator])
def accepter_reclamation(request, pk):
    """
    POST /api/reclamations/{id}/accepter/
    Coordinator: accept reclamation, triggers audit log + notification.
    """
    try:
        reclamation = Reclamation.objects.get(pk=pk)
    except Reclamation.DoesNotExist:
        return Response({"detail": "Réclamation introuvable."}, status=status.HTTP_404_NOT_FOUND)

    serializer = ReclamationDecisionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    ancien_statut = reclamation.statut
    nouvelle_note = serializer.validated_data.get('nouvelle_note')

    with transaction.atomic():
        # Update reclamation
        reclamation.statut = StatutReclamation.ACCEPTEE
        reclamation.commentaire_decision = serializer.validated_data['commentaire_decision']
        reclamation.date_traitement = timezone.now()
        reclamation.coordonnateur = request.user

        if nouvelle_note is not None:
            reclamation.nouvelle_note = nouvelle_note

            # Create audit log for note change
            note = reclamation.note_elementaire
            if note:
                AuditLog.objects.create(
                    note_elementaire=note,
                    reclamation=reclamation,
                    ancienne_valeur=note.valeur_note,
                    nouvelle_valeur=nouvelle_note,
                    auteur=request.user,
                    commentaire=f"Modification suite à réclamation #{reclamation.id}",
                )
                # Update the actual note value
                note.valeur_note = nouvelle_note
                note.save()

        reclamation.save()

        # Create status history
        HistoriqueStatut.objects.create(
            reclamation=reclamation,
            statut_precedent=ancien_statut,
            nouveau_statut=StatutReclamation.ACCEPTEE,
            modifie_par=request.user,
            commentaire=serializer.validated_data['commentaire_decision'],
        )

        # Create notification for student
        Notification.objects.create(
            destinataire=reclamation.etudiant,
            reclamation=reclamation,
            contenu=f"Votre réclamation #{reclamation.id} a été acceptée.",
            type_notification='ACCEPTATION',
        )

    detail_serializer = ReclamationDetailSerializer(reclamation)
    return Response(detail_serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsCoordinator])
def rejeter_reclamation(request, pk):
    """
    POST /api/reclamations/{id}/rejeter/
    Coordinator: reject reclamation, triggers notification.
    """
    try:
        reclamation = Reclamation.objects.get(pk=pk)
    except Reclamation.DoesNotExist:
        return Response({"detail": "Réclamation introuvable."}, status=status.HTTP_404_NOT_FOUND)

    serializer = ReclamationDecisionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    ancien_statut = reclamation.statut

    with transaction.atomic():
        reclamation.statut = StatutReclamation.REJETEE
        reclamation.commentaire_decision = serializer.validated_data['commentaire_decision']
        reclamation.date_traitement = timezone.now()
        reclamation.coordonnateur = request.user
        reclamation.save()

        HistoriqueStatut.objects.create(
            reclamation=reclamation,
            statut_precedent=ancien_statut,
            nouveau_statut=StatutReclamation.REJETEE,
            modifie_par=request.user,
            commentaire=serializer.validated_data['commentaire_decision'],
        )

        Notification.objects.create(
            destinataire=reclamation.etudiant,
            reclamation=reclamation,
            contenu=f"Votre réclamation #{reclamation.id} a été rejetée. Motif: {serializer.validated_data['commentaire_decision']}",
            type_notification='REJET',
        )

    detail_serializer = ReclamationDetailSerializer(reclamation)
    return Response(detail_serializer.data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsCoordinator])
def envoyer_professeur(request, pk):
    """
    POST /api/coordinator/reclamations/{id}/envoyer-professeur/
    Corps attendu : { "enseignant_id": <id> }
    """
    try:
        reclamation = Reclamation.objects.get(pk=pk)
    except Reclamation.DoesNotExist:
        return Response({"detail": "Réclamation introuvable."}, status=status.HTTP_404_NOT_FOUND)

    prof_id = request.data.get('enseignant_id')
    if not prof_id:
        return Response({"detail": "L'identifiant du professeur est requis."}, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        prof = User.objects.get(id=prof_id, role='ENSEIGNANT')
    except User.DoesNotExist:
        return Response({"detail": "Professeur introuvable."}, status=status.HTTP_404_NOT_FOUND)

    if reclamation.statut not in [StatutReclamation.EN_COURS, StatutReclamation.EN_ATTENTE]:
        return Response({"detail": "Cette réclamation ne peut pas être envoyée pour révision."}, status=status.HTTP_400_BAD_REQUEST)

    ancien_statut = reclamation.statut
    with transaction.atomic():
        reclamation.statut = StatutReclamation.EN_REVISION_ENSEIGNANT
        reclamation.enseignant_assigne = prof
        reclamation.save()

        HistoriqueStatut.objects.create(
            reclamation=reclamation,
            statut_precedent=ancien_statut,
            nouveau_statut=StatutReclamation.EN_REVISION_ENSEIGNANT,
            modifie_par=request.user,
            commentaire=f"Envoyé pour révision au professeur {prof.get_full_name() or prof.matricule}",
        )
        
        Notification.objects.create(
            destinataire=prof,
            reclamation=reclamation,
            contenu=f"Une nouvelle réclamation #{reclamation.id} nécessite votre révision.",
            type_notification='INFORMATION',
        )

    return Response(ReclamationDetailSerializer(reclamation).data)