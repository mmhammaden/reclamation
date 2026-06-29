"""
Custom permissions for Reclamations ISCAE.
- IsOwnerOrCoordinator: RG confidentiality
- IsModuleTeacher: Enseignant scope filter
- IsAdmin: role-based admin check (not is_staff)
"""
from rest_framework import permissions
from apps.users.models import Role


class IsOwnerOrCoordinator(permissions.BasePermission):
    """
    Object-level permission:
    - Étudiant: can only access own reclamations/notes
    - Coordinateur/Admin: can access all
    - Enseignant: can access reclamations for their modules
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        # Admin and coordinator can access everything
        if user.role in (Role.ADMIN, Role.COORDINATEUR):
            return True
        # Étudiant can only access their own
        if hasattr(obj, 'etudiant'):
            return obj.etudiant == user
        return False


class IsModuleTeacher(permissions.BasePermission):
    """
    Permission for Enseignant role.
    Teacher can only see reclamations for modules they teach.
    """

    def has_permission(self, request, view):
        return request.user.role == Role.ENSEIGNANT


class IsCoordinator(permissions.BasePermission):
    """Only COORDINATEUR role can access."""

    def has_permission(self, request, view):
        return request.user.role == Role.COORDINATEUR


class IsEtudiant(permissions.BasePermission):
    """Only ETUDIANT role can access."""

    def has_permission(self, request, view):
        return request.user.role == Role.ETUDIANT


class IsAdmin(permissions.BasePermission):
    """Only ADMIN role can access (checks role field, not is_staff)."""

    def has_permission(self, request, view):
        return request.user.role == Role.ADMIN