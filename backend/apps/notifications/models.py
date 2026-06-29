"""
Notification model for in-app and FCM push notifications.
"""
from django.db import models
from django.conf import settings


class TypeNotification(models.TextChoices):
    ACCEPTATION = 'ACCEPTATION', 'Acceptation'
    REJET = 'REJET', 'Rejet'
    NOUVELLE_RECLAMATION = 'NOUVELLE_RECLAMATION', 'Nouvelle réclamation'
    RAPPEL_RETARD = 'RAPPEL_RETARD', 'Rappel de retard'
    INFORMATION = 'INFORMATION', 'Information'


class Notification(models.Model):
    """
    Notification sent to a user.
    Can be in-app (estLu) and/or FCM push.
    """
    destinataire = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name="Destinataire",
    )
    reclamation = models.ForeignKey(
        'reclamations.Reclamation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications',
        verbose_name="Réclamation liée",
    )
    type_notification = models.CharField(
        max_length=30,
        choices=TypeNotification.choices,
        default=TypeNotification.INFORMATION,
        verbose_name="Type de notification",
    )
    contenu = models.TextField(
        verbose_name="Contenu",
        help_text="Message de la notification",
    )
    est_lu = models.BooleanField(
        default=False,
        verbose_name="Lu",
    )
    date_creation = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création",
    )
    date_lecture = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de lecture",
    )
    fcm_message_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="ID message FCM",
        help_text="Identifiant du message Firebase Cloud Messaging",
    )

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-date_creation']

    def __str__(self):
        return f"Notification pour {self.destinataire.matricule}: {self.contenu[:50]}"

    def marquer_comme_lu(self):
        from django.utils import timezone
        self.est_lu = True
        self.date_lecture = timezone.now()
        self.save(update_fields=['est_lu', 'date_lecture'])