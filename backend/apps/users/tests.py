from django.test import TestCase
from apps.users.models import User, Role


class UserCreationTest(TestCase):
    def test_create_user_with_matricule(self):
        u = User.objects.create_user(
            matricule='E999', email='e999@iscae.mr',
            password='secret', role=Role.ETUDIANT,
        )
        self.assertEqual(u.matricule, 'E999')
        self.assertTrue(u.check_password('secret'))
        self.assertEqual(u.role, Role.ETUDIANT)

    def test_matricule_is_unique(self):
        User.objects.create_user(
            matricule='E100', email='e100@iscae.mr', password='x',
        )
        with self.assertRaises(Exception):
            User.objects.create_user(
                matricule='E100', email='e101@iscae.mr', password='x',
            )