"""
Reclamation models - Core business domain.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .business_hours import add_business_hours


class StatutReclamation(models.TextChoices):
    EN_ATTENTE = 'EN_ATTENTE', 'En attente'
    EN_COURS = 'EN_COURS', 'En cours'
    ACCEPTEE = 'ACCEPTEE', 'Acceptée'
    REJETEE = 'REJETEE', 'Rejetée'
    ARCHIVEE = 'ARCHIVEE', 'Archivée'


class MotifReclamation(models.TextChoices):
    ERREUR_SAISIE = 'ERREUR_SAISIE', 'Erreur de saisie'
    OUBLI_NOTE = 'OUBLI_NOTE', 'Oubli de note'
    VERIFICATION_COPIE = 'VERIFICATION_COPIE', 'Demande de vérification de copie'
    AUTRE = 'AUTRE', 'Autre motif'


class Reclamation(models.Model):
    """
    Core reclamation entity.
    RG-01: dateLimiteTraitement = dateCreation + 72h
    RG-02: Un étudiant ne peut avoir qu'une réclamation active par note
    RG-03: Blocage si réclamation déjà acceptée pour cette note
    """


    motif = models.CharField(
        max_length=30,
        choices=MotifReclamation.choices,
        verbose_name="Motif",
    )
    statut = models.CharField(
        max_length=20,
        choices=StatutReclamation.choices,
        default=StatutReclamation.EN_ATTENTE,
        verbose_name="Statut",
    )
    description = models.TextField(
        verbose_name="Description",
        help_text="Description détaillée de la réclamation",
        blank=True,
    )
    commentaire_decision = models.TextField(
        verbose_name="Commentaire de décision",
        help_text="Commentaire obligatoire lors de l'acceptation/rejet",
        blank=True,
    )

    # Relations
    etudiant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reclamations',
        verbose_name="Étudiant",
        limit_choices_to={'role': 'ETUDIANT'},
    )
    note_elementaire = models.ForeignKey(
        'notes.NoteElementaire',
        on_delete=models.SET_NULL,
        null=True,
        related_name='reclamations',
        verbose_name="Note concernée",
    )
    coordonnateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reclamations_traitees',
        verbose_name="Traité par",
    )

    # Dates
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_limite_traitement = models.DateTimeField(verbose_name="Date limite de traitement")
    date_traitement = models.DateTimeField(null=True, blank=True, verbose_name="Date de traitement")

    note_originale = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name="Note originale",
        help_text="Valeur de la note au moment de la réclamation",
    )
    nouvelle_note = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name="Nouvelle note",
        help_text="Nouvelle valeur si la note a été modifiée",
    )

    enseignant_assigne = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reclamations_assignees',
        verbose_name="Professeur assigné",
        limit_choices_to={'role': 'ENSEIGNANT'},
    )
    commentaire_professeur = models.TextField(
        verbose_name="Commentaire du professeur",
        blank=True,
    )

    class Meta:
        verbose_name = "Réclamation"
        verbose_name_plural = "Réclamations"
        ordering = ['-date_creation']
        indexes = [
            models.Index(fields=['statut']),
            models.Index(fields=['etudiant', 'statut']),
            models.Index(fields=['date_limite_traitement']),
        ]

    def __str__(self):
        return f"Réclamation #{self.id} - {self.etudiant.matricule} - {self.motif}"

    def save(self, *args, **kwargs):
        """Auto-set date_limite_traitement on creation (RG-01: 72h ouvrées)."""
        if not self.pk and not self.date_limite_traitement:
            self.date_limite_traitement = add_business_hours(timezone.now(), hours_to_add=72)
        super().save(*args, **kwargs)

    def est_en_retard(self):
        """Check if reclamation is overdue (RG-01: past business-hours deadline)."""
        if self.statut in (StatutReclamation.ACCEPTEE, StatutReclamation.REJETEE, StatutReclamation.ARCHIVEE):
            return False
        from .business_hours import is_past_business_deadline
        return is_past_business_deadline(self.date_limite_traitement)

    def peut_etre_modifiee(self):
        """RG-02/03: Only EN_ATTENTE reclamations can be modified."""
        return self.statut == StatutReclamation.EN_ATTENTE


class PieceJointe(models.Model):
    """
    Attached file for a reclamation (<<extend>>).
    """
    reclamation = models.ForeignKey(
        Reclamation,
        on_delete=models.CASCADE,
        related_name='pieces_jointes',
        verbose_name="Réclamation",
    )
    fichier = models.FileField(
        upload_to='pieces_jointes/%Y/%m/',
        verbose_name="Fichier",
        help_text="Pièce jointe (PDF, image)",
    )
    nom_fichier = models.CharField(max_length=255, verbose_name="Nom du fichier")
    taille = models.PositiveIntegerField(default=0, verbose_name="Taille (octets)")
    date_ajout = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")

    class Meta:
        verbose_name = "Pièce jointe"
        verbose_name_plural = "Pièces jointes"

    def __str__(self):
        return self.nom_fichier


class HistoriqueStatut(models.Model):
    """
    Status transition history - written on every state change.
    """
    reclamation = models.ForeignKey(
        Reclamation,
        on_delete=models.CASCADE,
        related_name='historique_statuts',
        verbose_name="Réclamation",
    )
    statut_precedent = models.CharField(
        max_length=20,
        choices=StatutReclamation.choices,
        verbose_name="Statut précédent",
        null=True,
        blank=True,
    )
    nouveau_statut = models.CharField(
        max_length=20,
        choices=StatutReclamation.choices,
        verbose_name="Nouveau statut",
    )
    commentaire = models.TextField(blank=True, verbose_name="Commentaire")
    modifie_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Modifié par",
    )
    date_modification = models.DateTimeField(auto_now_add=True, verbose_name="Date de modification")

    class Meta:
        verbose_name = "Historique des statuts"
        verbose_name_plural = "Historique des statuts"
        ordering = ['-date_modification']

    def __str__(self):
        return f"{self.reclamation.id}: {self.statut_precedent} → {self.nouveau_statut}"

# FILE: backend/apps/reclamations/models.py

class StatutReclamation(models.TextChoices):
    EN_ATTENTE = 'EN_ATTENTE', 'En attente'
    EN_COURS = 'EN_COURS', 'En cours'
    EN_REVISION_ENSEIGNANT = 'EN_REVISION_ENSEIGNANT', 'En révision par le professeur' # <-- Nouveau statut
    ACCEPTEE = 'ACCEPTEE', 'Acceptée'
    REJETEE = 'REJETEE', 'Rejetée'
    ARCHIVEE = 'ARCHIVEE', 'Archivée'
