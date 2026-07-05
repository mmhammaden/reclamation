from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta
from apps.users.models import User, Role
from apps.notes.models import NoteElementaire
from .models import Reclamation, StatutReclamation, MotifReclamation


def make_user(matricule, role=Role.ETUDIANT, password='pass1234'):
    u = User.objects.create_user(
        matricule=matricule, email=f'{matricule}@iscae.ma',
        password=password, role=role,
        first_name='Test', last_name='User',
    )
    return u


def make_note(etudiant):
    return NoteElementaire.objects.create(
        etudiant=etudiant, code_module='INF-101',
        nom_module='Informatique', semestre='S1',
        annee_academique='2024-2025', valeur_note=12.00,
    )


def make_reclamation(etudiant, note, statut=StatutReclamation.EN_ATTENTE):
    return Reclamation.objects.create(
        etudiant=etudiant, note_elementaire=note,
        motif=MotifReclamation.ERREUR_SAISIE,
        description='Test',
        statut=statut,
        date_limite_traitement=timezone.now() + timedelta(hours=72),
    )


class ReclamationModelTest(TestCase):
    def setUp(self):
        self.etudiant = make_user('E001')
        self.note = make_note(self.etudiant)

    def test_date_limite_auto_set_on_creation(self):
        rec = make_reclamation(self.etudiant, self.note)
        self.assertIsNotNone(rec.date_limite_traitement)

    def test_peut_etre_modifiee_en_attente(self):
        rec = make_reclamation(self.etudiant, self.note, StatutReclamation.EN_ATTENTE)
        self.assertTrue(rec.peut_etre_modifiee())

    def test_peut_etre_modifiee_false_when_accepted(self):
        rec = make_reclamation(self.etudiant, self.note, StatutReclamation.ACCEPTEE)
        self.assertFalse(rec.peut_etre_modifiee())

    def test_est_en_retard_false_for_closed_statuts(self):
        for s in (StatutReclamation.ACCEPTEE, StatutReclamation.REJETEE, StatutReclamation.ARCHIVEE):
            rec = make_reclamation(self.etudiant, self.note, s)
            self.assertFalse(rec.est_en_retard())


class ReclamationAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.etudiant = make_user('E002')
        self.coord = make_user('C001', role=Role.COORDINATEUR)
        self.note = make_note(self.etudiant)
        self.client.force_authenticate(user=self.etudiant)

    def test_create_reclamation(self):
        resp = self.client.post('/api/reclamations/create/', {
            'motif': 'ERREUR_SAISIE',
            'description': 'Note incorrecte',
            'note_elementaire': self.note.id,
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_rg02_duplicate_active_reclamation_blocked(self):
        make_reclamation(self.etudiant, self.note)
        resp = self.client.post('/api/reclamations/create/', {
            'motif': 'OUBLI_NOTE',
            'description': 'Doublon',
            'note_elementaire': self.note.id,
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rg03_accepted_reclamation_blocks_new(self):
        make_reclamation(self.etudiant, self.note, StatutReclamation.ACCEPTEE)
        resp = self.client.post('/api/reclamations/create/', {
            'motif': 'ERREUR_SAISIE',
            'description': 'Après acceptation',
            'note_elementaire': self.note.id,
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_returns_only_own_reclamations(self):
        other = make_user('E003')
        other_note = make_note(other)
        make_reclamation(self.etudiant, self.note)
        make_reclamation(other, other_note)
        resp = self.client.get('/api/reclamations/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        ids = [r['id'] for r in resp.data['results']]
        reclamations = Reclamation.objects.filter(etudiant=self.etudiant)
        for rec in reclamations:
            self.assertIn(rec.id, ids)

    def test_delete_en_attente_allowed(self):
        rec = make_reclamation(self.etudiant, self.note)
        resp = self.client.delete(f'/api/reclamations/{rec.id}/delete/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_en_cours_blocked(self):
        rec = make_reclamation(self.etudiant, self.note, StatutReclamation.EN_COURS)
        resp = self.client.delete(f'/api/reclamations/{rec.id}/delete/')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_access_denied(self):
        self.client.force_authenticate(user=None)
        resp = self.client.get('/api/reclamations/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_coordinator_can_accept(self):
        rec = make_reclamation(self.etudiant, self.note, StatutReclamation.EN_COURS)
        self.client.force_authenticate(user=self.coord)
        resp = self.client.post(f'/api/coordinator/reclamations/{rec.id}/accepter/', {
            'commentaire_decision': 'Note corrigée',
            'nouvelle_note': 15.00,
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        rec.refresh_from_db()
        self.assertEqual(rec.statut, StatutReclamation.ACCEPTEE)

    def test_coordinator_can_reject(self):
        rec = make_reclamation(self.etudiant, self.note, StatutReclamation.EN_COURS)
        self.client.force_authenticate(user=self.coord)
        resp = self.client.post(f'/api/coordinator/reclamations/{rec.id}/rejeter/', {
            'commentaire_decision': 'Non justifié',
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        rec.refresh_from_db()
        self.assertEqual(rec.statut, StatutReclamation.REJETEE)

    def test_etudiant_cannot_access_coordinator_endpoint(self):
        rec = make_reclamation(self.etudiant, self.note)
        resp = self.client.post(f'/api/coordinator/reclamations/{rec.id}/accepter/', {
            'commentaire_decision': 'Tentative',
        })
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class UserModelTest(TestCase):
    def test_role_helpers(self):
        e = make_user('E010', Role.ETUDIANT)
        c = make_user('C010', Role.COORDINATEUR)
        a = make_user('A010', Role.ADMIN)
        t = make_user('T010', Role.ENSEIGNANT)
        self.assertTrue(e.is_etudiant())
        self.assertFalse(e.is_coordinateur())
        self.assertTrue(c.is_coordinateur())
        self.assertTrue(a.is_admin())
        self.assertTrue(t.is_enseignant())