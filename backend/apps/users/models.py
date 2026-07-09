"""
User model for Reclamations ISCAE.
Roles: ETUDIANT, COORDINATEUR, ADMIN, ENSEIGNANT
"""
from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager


class Role(models.TextChoices):
    ETUDIANT = 'ETUDIANT', 'Étudiant'
    COORDINATEUR = 'COORDINATEUR', 'Coordinateur'
    ADMIN = 'ADMIN', 'Administrateur'
    ENSEIGNANT = 'ENSEIGNANT', 'Enseignant'


class User(AbstractUser):
    """
    Custom user model with matricule as unique identifier and role enum.
    """
    username = None  # Remove username, use matricule as identifier
    matricule = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Matricule",
        help_text="Numéro de matricule unique de l'étudiant/employé",
    )
    email = models.EmailField(
        unique=True,
        verbose_name="Email",
        help_text="Adresse email institutionnelle",
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.ETUDIANT,
        verbose_name="Rôle",
        help_text="Rôle dans le système",
    )
    telephone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Téléphone",
    )
    modules_enseignes = models.ManyToManyField(
        'notes.NoteElementaire',
        blank=True,
        related_name='enseignants',
        verbose_name="Modules enseignés",
        help_text="Modules que cet enseignant est autorisé à consulter",
    )
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'matricule'
    REQUIRED_FIELDS = ['email', 'role']

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ['matricule']

    def __str__(self):
        return f"{self.matricule} - {self.get_full_name() or self.email}"

    def is_etudiant(self):
        return self.role == Role.ETUDIANT

    def is_coordinateur(self):
        return self.role == Role.COORDINATEUR

    def is_admin(self):
        return self.role == Role.ADMIN

    def is_enseignant(self):
        return self.role == Role.ENSEIGNANT