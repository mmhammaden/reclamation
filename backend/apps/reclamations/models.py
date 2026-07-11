"""
Reclamation models - Core business domain.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from .business_hours import add_business_hours


class StatutReclamation(models.TextChoices):
    EN_ATTENTE = 'EN_ATTENTE', 'En attente'
    EN_COURS = 'EN_COURS', 'En cours'
    EN_REVISION_ENSEIGNANT = 'EN_REVISION_ENSEIGNANT', 'En révision par le professeur'
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
    Une réclamation globale pouvant couvrir plusieurs matières (LigneReclamation).
    RG-01: date_limite_traitement = date_creation + 72h ouvrées
    RG-02: Un étudiant ne peut avoir qu'une réclamation active à la fois
    """
    statut = models.CharField(
        max_length=30,
        choices=StatutReclamation.choices,
        default=StatutReclamation.EN_ATTENTE,
    )
    description = models.TextField(blank=True)
    commentaire_decision = models.TextField(blank=True)

    etudiant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reclamations',
        limit_choices_to={'role': 'ETUDIANT'},
    )
    coordonnateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='reclamations_traitees',
    )
    enseignant_assigne = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='reclamations_assignees',
        limit_choices_to={'role': 'ENSEIGNANT'},
    )
    commentaire_professeur = models.TextField(blank=True)

    date_creation = models.DateTimeField(auto_now_add=True)
    date_limite_traitement = models.DateTimeField()
    date_traitement = models.DateTimeField(null=True, blank=True)

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
        return f"Réclamation #{self.id} - {self.etudiant.matricule}"

    def save(self, *args, **kwargs):
        if not self.pk and not self.date_limite_traitement:
            self.date_limite_traitement = add_business_hours(timezone.now(), hours_to_add=72)
        super().save(*args, **kwargs)

    def est_en_retard(self):
        if self.statut in (StatutReclamation.ACCEPTEE, StatutReclamation.REJETEE, StatutReclamation.ARCHIVEE):
            return False
        from .business_hours import is_past_business_deadline
        return is_past_business_deadline(self.date_limite_traitement)

    def peut_etre_modifiee(self):
        return self.statut == StatutReclamation.EN_ATTENTE


class TypeNoteReclamation(models.TextChoices):
    CONTINU = 'CONTINU', 'Continu (CC)'
    FINAL = 'FINAL', 'Final (Examen)'


class LigneReclamation(models.Model):
    """
    Une ligne = un élément de module dans la réclamation.
    Chaque ligne cible soit la note de Continu, soit la note de Final.
    Chaque ligne a son propre motif et conserve la note originale.
    """
    reclamation = models.ForeignKey(
        Reclamation,
        on_delete=models.CASCADE,
        related_name='lignes',
    )
    element_module = models.ForeignKey(
        'notes.ElementModule',
        on_delete=models.SET_NULL,
        null=True,
        related_name='lignes_reclamation',
    )
    type_note = models.CharField(
        max_length=10,
        choices=TypeNoteReclamation.choices,
        default=TypeNoteReclamation.CONTINU,
        verbose_name="Type de note",
        help_text="Continu (CC) ou Final (Examen)",
    )
    motif = models.CharField(max_length=30, choices=MotifReclamation.choices)
    note_originale = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    nouvelle_note = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Ligne de réclamation"
        verbose_name_plural = "Lignes de réclamation"
        # RG-02: un élément ne peut apparaître qu'une fois par réclamation
        unique_together = ['reclamation', 'element_module', 'type_note']

    def __str__(self):
        return f"Ligne #{self.id} - {self.element_module} ({self.get_type_note_display()})"

    def get_note_originale(self):
        """Get the original note based on type_note."""
        if not self.element_module:
            return None
        if self.type_note == TypeNoteReclamation.CONTINU:
            return self.element_module.note_continu
        return self.element_module.note_final


class PieceJointe(models.Model):
    reclamation = models.ForeignKey(
        Reclamation,
        on_delete=models.CASCADE,
        related_name='pieces_jointes',
    )
    ligne = models.ForeignKey(
        'LigneReclamation',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='pieces_jointes',
    )
    fichier = models.FileField(upload_to='pieces_jointes/%Y/%m/')
    nom_fichier = models.CharField(max_length=255)
    taille = models.PositiveIntegerField(default=0)
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Pièce jointe"
        verbose_name_plural = "Pièces jointes"

    def __str__(self):
        return self.nom_fichier


class HistoriqueStatut(models.Model):
    reclamation = models.ForeignKey(
        Reclamation,
        on_delete=models.CASCADE,
        related_name='historique_statuts',
    )
    statut_precedent = models.CharField(
        max_length=30, choices=StatutReclamation.choices, null=True, blank=True,
    )
    nouveau_statut = models.CharField(max_length=30, choices=StatutReclamation.choices)
    commentaire = models.TextField(blank=True)
    modifie_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
    )
    date_modification = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Historique des statuts"
        verbose_name_plural = "Historique des statuts"
        ordering = ['-date_modification']

    def __str__(self):
        return f"{self.reclamation.id}: {self.statut_precedent} → {self.nouveau_statut}"