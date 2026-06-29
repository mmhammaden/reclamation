"""
AuditLog model - Immutable record of all note modifications.
"""
from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    """
    Immutable audit trail for note modifications.
    Written automatically when a coordinator modifies a note.
    """
    note_elementaire = models.ForeignKey(
        'notes.NoteElementaire',
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs',
        verbose_name="Note concernée",
    )
    reclamation = models.ForeignKey(
        'reclamations.Reclamation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name="Réclamation liée",
    )
    ancienne_valeur = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Ancienne valeur",
    )
    nouvelle_valeur = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Nouvelle valeur",
    )
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Auteur de la modification",
    )
    commentaire = models.TextField(
        blank=True,
        verbose_name="Commentaire",
    )
    date_modification = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de modification",
    )

    class Meta:
        verbose_name = "Journal d'audit"
        verbose_name_plural = "Journaux d'audit"
        ordering = ['-date_modification']
        # Immutable: no update or delete
        permissions = [
            ("cannot_delete_auditlog", "Cannot delete audit logs"),
        ]

    def __str__(self):
        return f"Audit #{self.id}: {self.ancienne_valeur} → {self.nouvelle_valeur} par {self.auteur}"

    def save(self, *args, **kwargs):
        """Prevent modification of existing audit logs."""
        if self.pk:
            raise PermissionError("Les journaux d'audit sont immuables et ne peuvent pas être modifiés.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Prevent deletion of audit logs."""
        raise PermissionError("Les journaux d'audit sont immuables et ne peuvent pas être supprimés.")