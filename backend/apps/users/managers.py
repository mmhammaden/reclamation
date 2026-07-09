"""
Custom user manager for Reclamations ISCAE.
Uses matricule as the unique identifier instead of username.
"""
from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """Custom manager where matricule is the unique identifier."""

    def create_user(self, matricule, email=None, password=None, **extra_fields):
        """Create and save a user with the given matricule, email and password."""
        if not matricule:
            raise ValueError("Le matricule est obligatoire")
        if email:
            email = self.normalize_email(email)
        user = self.model(matricule=matricule, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, matricule, email=None, password=None, **extra_fields):
        """Create and save a superuser with the given matricule, email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(matricule, email, password, **extra_fields)