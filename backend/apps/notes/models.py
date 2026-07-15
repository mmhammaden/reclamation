"""
Note models - Flattened structure: ResultatSemestre → ElementModule
Data is imported from external PV (procès-verbal) files.
This is a read-only model - no create/update via API.
"""
from django.db import models
from django.conf import settings
from decimal import Decimal


class ResultatSemestre(models.Model):
    """
    Semester result for a student.
    moy_semestre and observation are computed from elements.
    """
    etudiant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='resultats_semestre',
        verbose_name="Étudiant",
        limit_choices_to={'role': 'ETUDIANT'},
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
    date_import = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date d'import",
    )

    class Meta:
        verbose_name = "Résultat de semestre"
        verbose_name_plural = "Résultats de semestres"
        unique_together = ['etudiant', 'semestre', 'annee_academique']
        ordering = ['-annee_academique', 'semestre']

    def __str__(self):
        return f"{self.etudiant.matricule} - {self.semestre} {self.annee_academique}: {self.moy_semestre}/20"

    @property
    def moy_semestre(self) -> Decimal:
        """Compute semester average from element averages weighted by credits."""
        elements = self.elements.all()
        if not elements:
            return Decimal('0')
        
        total_credits = sum(e.credit for e in elements)
        if total_credits == 0:
            return Decimal('0')
        
        weighted_sum = sum(e.note_moyenne * e.credit for e in elements)
        return (weighted_sum / total_credits).quantize(Decimal('0.01'))

    @property
    def observation(self) -> str:
        """Compute observation: Validé if moy_semestre >= 10, else Rattrapage."""
        return 'Validé' if self.moy_semestre >= 10 else 'Rattrapage'


class ElementModule(models.Model):
    """
    Element (e.g. MIAG311, MIAG312) with Continu (CC), Final (exam), Credit.
    Now directly linked to ResultatSemestre (flattened structure).
    note_moyenne and observation are computed.
    """
    resultat_semestre = models.ForeignKey(
        ResultatSemestre,
        on_delete=models.CASCADE,
        related_name='elements',
        verbose_name="Résultat de semestre",
    )
    code_element = models.CharField(
        max_length=20,
        verbose_name="Code Élément",
        help_text="Code unique de l'élément (ex: MIAG311)",
    )
    nom_matiere = models.CharField(
        max_length=200,
        verbose_name="Nom de la matière",
        blank=True,
        help_text="Nom de l'élément/matière (ex: Frameworks JEE)",
    )
    note_continu = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Note Continu (CC)",
        help_text="Note de contrôle continu sur 20",
    )
    note_final = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Note Finale (Examen)",
        help_text="Note d'examen sur 20",
    )
    credit = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        verbose_name="Crédit",
        help_text="Crédit de l'élément",
    )

    class Meta:
        verbose_name = "Élément de module"
        verbose_name_plural = "Éléments de module"
        unique_together = ['resultat_semestre', 'code_element']
        ordering = ['code_element']

    def __str__(self):
        return f"{self.code_element} - {self.note_moyenne}/20"

    @property
    def note_moyenne(self) -> Decimal:
        """Compute element average: (note_continu + note_final) / 2."""
        return ((self.note_continu + self.note_final) / 2).quantize(Decimal('0.01'))

    @property
    def observation(self) -> str:
        """Compute observation: Validé if average >= 10, else Rattrapage."""
        return 'Validé' if self.note_moyenne >= 10 else 'Rattrapage'