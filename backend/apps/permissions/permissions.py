"""
Permissions for Reclamations ISCAE.
Re-exports permissions from reclamations app for testing.
"""
from apps.reclamations.permissions import (
    IsOwnerOrCoordinator,
    IsEtudiant,
    IsCoordinator,
    IsModuleTeacher,
    IsAdmin,
)

__all__ = [
    'IsOwnerOrCoordinator',
    'IsEtudiant',
    'IsCoordinator',
    'IsModuleTeacher',
    'IsAdmin',
]