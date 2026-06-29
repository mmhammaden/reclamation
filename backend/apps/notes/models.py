"""
NoteElementaire model - Read-only external notes imported via admin.
"""
from django.db import models
from django.conf import settings


class NoteElementaire(models.Model):
    """
    Represents a student's grade for a specific module.
    Data is imported from external PV (procès-verbal) files.
    This is a read-only model - no create/update via API.
    """
    etudiant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name="Étudiant",
        limit_choices_to={'role': 'ETUDIANT'},
    )
    code_module = models.CharField(
        max_length=20,
        verbose_name="Code Module",
        help_text="Code unique du module (ex: INF-2024)",
    )
    nom_module = models.CharField(
        max_length=200,
        verbose_name="Nom du module",
        blank=True,
    )
    semestre = models.CharField(
        max_length=20,
        verbose_name="Semestre",
        help_text="Semestre concerné (ex: S1, S2)",
    )
    annee_academique = models.CharField(
        max_length=20,
        verbose_name="Année académique",
        help_text="Ex: 2024-2025",
    )
    valeur_note = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Note",
        help_text="Note sur 20",
    )
    coefficient = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=1.0,
        verbose_name="Coefficient",
    )
    date_import = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date d'import",
    )
    est_verouillee = models.BooleanField(
        default=False,
        verbose_name="Note verrouillée",
        help_text="Si True, la note ne peut plus être modifiée",
    )

    class Meta:
        verbose_name = "Note élémentaire"
        verbose_name_plural = "Notes élémentaires"
        unique_together = ['etudiant', 'code_module', 'semestre', 'annee_academique']
        ordering = ['-annee_academique', 'code_module']

    def __str__(self):
        return f"{self.etudiant.matricule} - {self.code_module}: {self.valeur_note}/20"