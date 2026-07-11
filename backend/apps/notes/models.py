"""
Note models - Hierarchical structure: ResultatSemestre → Module → ElementModule
Data is imported from external PV (procès-verbal) files.
This is a read-only model - no create/update via API.
"""
from django.db import models
from django.conf import settings


class ResultatSemestre(models.Model):
    """
    Semester result for a student.
    Contains moy_semestre, observation (Validé/Rattrapage).
    """
    etudiant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='resultats_semestre',
        verbose_name="Étudiant",
        limit_choices_to={'role': 'ETUDIANT'},
    )
    moy_semestre = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Moyenne du semestre",
        help_text="Moyenne générale sur 20",
    )
    observation = models.CharField(
        max_length=20,
        verbose_name="Observation",
        help_text="Validé ou Rattrapage",
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


class Module(models.Model):
    """
    Module (e.g. MIAG31) with its average, final note, credit, and observation.
    """
    resultat_semestre = models.ForeignKey(
        ResultatSemestre,
        on_delete=models.CASCADE,
        related_name='modules',
        verbose_name="Résultat de semestre",
    )
    code_module = models.CharField(
        max_length=20,
        verbose_name="Code Module",
        help_text="Code unique du module (ex: MIAG31)",
    )
    nom_module = models.CharField(
        max_length=200,
        verbose_name="Nom du module",
        blank=True,
    )
    moy_module = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Moyenne du module",
        help_text="Moyenne sur 20",
    )
    note_finale = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Note finale",
        help_text="Note finale sur 20",
    )
    credit = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        verbose_name="Crédit",
        help_text="Crédit du module",
    )
    observation = models.CharField(
        max_length=20,
        verbose_name="Observation",
        help_text="Validé ou Rattrapage",
    )

    class Meta:
        verbose_name = "Module"
        verbose_name_plural = "Modules"
        unique_together = ['resultat_semestre', 'code_module']
        ordering = ['code_module']

    def __str__(self):
        return f"{self.code_module} - {self.moy_module}/20"


class ElementModule(models.Model):
    """
    Element (e.g. MIAG311, MIAG312) with Continu (CC), Final (exam), Note (moyenne), Credit, Obs.
    """
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='elements',
        verbose_name="Module",
    )
    code_element = models.CharField(
        max_length=20,
        verbose_name="Code Élément",
        help_text="Code unique de l'élément (ex: MIAG311)",
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
    note_moyenne = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Note Moyenne",
        help_text="Moyenne de l'élément sur 20",
    )
    credit = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        verbose_name="Crédit",
        help_text="Crédit de l'élément",
    )
    observation = models.CharField(
        max_length=20,
        verbose_name="Observation",
        help_text="Validé ou Rattrapage",
    )

    class Meta:
        verbose_name = "Élément de module"
        verbose_name_plural = "Éléments de module"
        unique_together = ['module', 'code_element']
        ordering = ['code_element']

    def __str__(self):
        return f"{self.code_element} - {self.note_moyenne}/20"