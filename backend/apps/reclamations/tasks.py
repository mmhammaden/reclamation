"""
Celery tasks for Reclamations ISCAE.
- Daily overdue reminder alerts (RG-01)
- FCM push notification sending
"""
import html
from celery import shared_task
from django.utils import timezone
from django.db.models import Q
from .models import Reclamation, StatutReclamation
from .business_hours import is_past_business_deadline


@shared_task
def envoyer_rappels_retard():
    """
    RG-01: Daily reminder alert to coordinators for overdue reclamations.
    Runs daily (e.g., 08:00) via Celery Beat.
    Finds all reclamations past their business-hours deadline that are
    still in EN_ATTENTE or EN_COURS status, and creates notifications.
    """
    from apps.notifications.models import Notification, TypeNotification
    from apps.users.models import User, Role

    overdue = Reclamation.objects.filter(
        statut__in=[StatutReclamation.EN_ATTENTE, StatutReclamation.EN_COURS],
        date_limite_traitement__lt=timezone.now(),
    ).select_related('etudiant', 'note_elementaire')

    coordinators = User.objects.filter(role=Role.COORDINATEUR)

    count = 0
    for reclamation in overdue:
        # Double-check with business hours logic
        if not is_past_business_deadline(reclamation.date_limite_traitement):
            continue

        for coord in coordinators:
            Notification.objects.create(
                destinataire=coord,
                reclamation=reclamation,
                type_notification=TypeNotification.RAPPEL_RETARD,
                contenu=(
                    f"Réclamation #{reclamation.id} en retard - "
                    f"{html.escape(reclamation.etudiant.matricule)} - "
                    f"{html.escape(reclamation.motif)} "
                    f"(délai dépassé le {reclamation.date_limite_traitement.strftime('%d/%m/%Y %H:%M')})"
                ),
            )
        count += 1

    return f"{count} rappels de retard envoyés à {coordinators.count()} coordinateur(s)"


@shared_task
def envoyer_notification_push(destinataire_id, titre, message, reclamation_id=None):
    """
    Send FCM push notification to a user.
    Falls back gracefully if FCM is not configured.
    """
    from apps.notifications.models import Notification, TypeNotification

    try:
        from firebase_admin import messaging, initialize_app, get_app
        try:
            app = get_app()
        except ValueError:
            initialize_app()

        # Escape user-provided content to prevent XSS
        safe_titre = html.escape(str(titre))
        safe_message = html.escape(str(message))

        message_data = {
            'title': safe_titre,
            'body': safe_message,
        }

        if reclamation_id:
            message_data['reclamation_id'] = str(reclamation_id)

        # Send to topic based on user role for simplicity
        # In production, use device tokens stored in FCMDevice model
        from apps.users.models import User
        user = User.objects.get(id=destinataire_id)

        msg = messaging.Message(
            notification=messaging.Notification(
                title=safe_titre,
                body=safe_message,
            ),
            data=message_data,
            topic=f"user_{destinataire_id}",
        )

        response = messaging.send(msg)
        return f"Push envoyé: {response}"

    except Exception as e:
        # FCM not configured or error - log and continue
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"FCM push non envoyé (FCM peut ne pas être configuré): {e}")
        return f"Push non envoyé: {e}"


@shared_task
def notifier_changement_statut(reclamation_id, nouveau_statut, modifie_par_id=None):
    """
    Send in-app notification (and push if available) when a reclamation
    status changes.
    """
    from apps.notifications.models import Notification, TypeNotification
    from apps.users.models import User

    try:
        reclamation = Reclamation.objects.get(id=reclamation_id)
    except Reclamation.DoesNotExist:
        return "Réclamation introuvable"

    # Map status to notification type
    type_map = {
        StatutReclamation.ACCEPTEE: TypeNotification.ACCEPTATION,
        StatutReclamation.REJETEE: TypeNotification.REJET,
    }
    notif_type = type_map.get(nouveau_statut, TypeNotification.INFORMATION)

    # Create in-app notification for the student
    statut_label = dict(StatutReclamation.choices).get(nouveau_statut, str(nouveau_statut)).lower()
    Notification.objects.create(
        destinataire=reclamation.etudiant,
        reclamation=reclamation,
        type_notification=notif_type,
        contenu=(
            f"Votre réclamation #{reclamation.id} a été "
            f"{html.escape(statut_label)}."
        ),
    )

    # Also notify coordinators if new reclamation
    if nouveau_statut == StatutReclamation.EN_ATTENTE:
        coordinators = User.objects.filter(role='COORDINATEUR')
        for coord in coordinators:
            Notification.objects.create(
                destinataire=coord,
                reclamation=reclamation,
                type_notification=TypeNotification.NOUVELLE_RECLAMATION,
                contenu=(
                    f"Nouvelle réclamation #{reclamation.id} de "
                    f"{html.escape(reclamation.etudiant.matricule)} - "
                    f"{html.escape(reclamation.motif)}"
                ),
            )

    # Try push notification (async, non-blocking)
    envoyer_notification_push.delay(
        destinataire_id=reclamation.etudiant.id,
        titre="Mise à jour de votre réclamation",
        message=f"Votre réclamation #{reclamation.id} a été mise à jour.",
        reclamation_id=reclamation.id,
    )

    return f"Notification envoyée pour réclamation #{reclamation_id}"
