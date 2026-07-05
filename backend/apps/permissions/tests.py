from django.test import TestCase
from rest_framework.test import APIRequestFactory
from apps.users.models import User, Role
from .permissions import IsEtudiant, IsCoordinator, IsOwnerOrCoordinator


def make_user(matricule, role=Role.ETUDIANT, password='pass1234'):
    return User.objects.create_user(
        matricule=matricule, email=f'{matricule}@iscae.ma',
        password=password, role=role,
        first_name='Test', last_name='User',
    )


class IsEtudiantPermissionTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.etudiant = make_user('E001', Role.ETUDIANT)
        self.coord = make_user('C001', Role.COORDINATEUR)
        self.admin = make_user('A001', Role.ADMIN)
        self.permission = IsEtudiant()

    def test_allows_etudiant(self):
        request = self.factory.get('/')
        request.user = self.etudiant
        self.assertTrue(self.permission.has_permission(request, None))

    def test_denies_coordinator(self):
        request = self.factory.get('/')
        request.user = self.coord
        self.assertFalse(self.permission.has_permission(request, None))

    def test_denies_admin(self):
        request = self.factory.get('/')
        request.user = self.admin
        self.assertFalse(self.permission.has_permission(request, None))


class IsCoordinatorPermissionTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.etudiant = make_user('E002', Role.ETUDIANT)
        self.coord = make_user('C002', Role.COORDINATEUR)
        self.admin = make_user('A002', Role.ADMIN)
        self.permission = IsCoordinator()

    def test_allows_coordinator(self):
        request = self.factory.get('/')
        request.user = self.coord
        self.assertTrue(self.permission.has_permission(request, None))

    def test_denies_etudiant(self):
        request = self.factory.get('/')
        request.user = self.etudiant
        self.assertFalse(self.permission.has_permission(request, None))

    def test_allows_admin(self):
        request = self.factory.get('/')
        request.user = self.admin
        self.assertTrue(self.permission.has_permission(request, None))


class IsOwnerOrCoordinatorPermissionTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.etudiant = make_user('E003', Role.ETUDIANT)
        self.other_etudiant = make_user('E004', Role.ETUDIANT)
        self.coord = make_user('C003', Role.COORDINATEUR)
        self.permission = IsOwnerOrCoordinator()

    def test_allows_owner(self):
        request = self.factory.get('/')
        request.user = self.etudiant
        view = type('MockView', (), {'kwargs': {'etudiant_id': self.etudiant.id}})()
        self.assertTrue(self.permission.has_object_permission(request, None, view))

    def test_denies_non_owner_etudiant(self):
        request = self.factory.get('/')
        request.user = self.other_etudiant
        view = type('MockView', (), {'kwargs': {'etudiant_id': self.etudiant.id}})()
        self.assertFalse(self.permission.has_object_permission(request, None, view))

    def test_allows_coordinator(self):
        request = self.factory.get('/')
        request.user = self.coord
        view = type('MockView', (), {'kwargs': {'etudiant_id': self.etudiant.id}})()
        self.assertTrue(self.permission.has_object_permission(request, None, view))