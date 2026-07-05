from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta
from apps.users.models import User, Role
from apps.notes.models import NoteElementaire
from .models import Reclamation, StatutReclamation, MotifReclamation, HistoriqueStatut


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


# Integration tests for core reclamations flow (create, assign, resolve)
class ReclamationIntegrationTest(TestCase):
    """
    End-to-end integration tests for the reclamations flow:
    1. Student creates a reclamation
    2. Coordinator assigns (traiter) the reclamation
    3. Coordinator resolves (accept/reject) the reclamation
    """

    def setUp(self):
        self.client = APIClient()
        self.etudiant = make_user('STUDENT001', Role.ETUDIANT)
        self.coord = make_user('COORD001', Role.COORDINATEUR)
        self.note = make_note(self.etudiant)

    def test_full_flow_create_assign_accept(self):
        """Test: Student creates -> Coordinator assigns -> Coordinator accepts"""
        # Step 1: Student creates a reclamation
        self.client.force_authenticate(user=self.etudiant)
        create_resp = self.client.post('/api/reclamations/create/', {
            'motif': 'ERREUR_SAISIE',
            'description': 'Note incorrecte, devrait être 15',
            'note_elementaire': self.note.id,
        })
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        reclamation_id = create_resp.data['id']

        # Verify reclamation was created with EN_ATTENTE status
        rec = Reclamation.objects.get(id=reclamation_id)
        self.assertEqual(rec.statut, StatutReclamation.EN_ATTENTE)
        self.assertIsNone(rec.coordonnateur)

        # Step 2: Coordinator assigns the reclamation (EN_ATTENTE -> EN_COURS)
        self.client.force_authenticate(user=self.coord)
        assign_resp = self.client.patch(f'/api/coordinator/reclamations/{reclamation_id}/traiter/')
        self.assertEqual(assign_resp.status_code, status.HTTP_200_OK)

        rec.refresh_from_db()
        self.assertEqual(rec.statut, StatutReclamation.EN_COURS)
        self.assertEqual(rec.coordonnateur, self.coord)

        # Verify status history was created
        historique = HistoriqueStatut.objects.filter(reclamation=rec)
        self.assertEqual(historique.count(), 2)  # Creation + assignment

        # Step 3: Coordinator accepts the reclamation (EN_COURS -> ACCEPTEE)
        accept_resp = self.client.post(f'/api/coordinator/reclamations/{reclamation_id}/accepter/', {
            'commentaire_decision': 'Note corrigée à 15',
            'nouvelle_note': 15.00,
        })
        self.assertEqual(accept_resp.status_code, status.HTTP_200_OK)

        rec.refresh_from_db()
        self.assertEqual(rec.statut, StatutReclamation.ACCEPTEE)
        self.assertEqual(rec.nouvelle_note, 15.00)
        self.assertIsNotNone(rec.date_traitement)

        # Verify final status history
        historique = HistoriqueStatut.objects.filter(reclamation=rec)
        self.assertEqual(historique.count(), 3)  # Creation + assignment + resolution

    def test_full_flow_create_assign_reject(self):
        """Test: Student creates -> Coordinator assigns -> Coordinator rejects"""
        # Step 1: Student creates a reclamation
        self.client.force_authenticate(user=self.etudiant)
        create_resp = self.client.post('/api/reclamations/create/', {
            'motif': 'OUBLI_NOTE',
            'description': 'Note oubliée',
            'note_elementaire': self.note.id,
        })
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        reclamation_id = create_resp.data['id']

        # Step 2: Coordinator assigns the reclamation
        self.client.force_authenticate(user=self.coord)
        assign_resp = self.client.patch(f'/api/coordinator/reclamations/{reclamation_id}/traiter/')
        self.assertEqual(assign_resp.status_code, status.HTTP_200_OK)

        rec = Reclamation.objects.get(id=reclamation_id)
        self.assertEqual(rec.statut, StatutReclamation.EN_COURS)

        # Step 3: Coordinator rejects the reclamation
        reject_resp = self.client.post(f'/api/coordinator/reclamations/{reclamation_id}/rejeter/', {
            'commentaire_decision': 'Justification insuffisante',
        })
        self.assertEqual(reject_resp.status_code, status.HTTP_200_OK)

        rec.refresh_from_db()
        self.assertEqual(rec.statut, StatutReclamation.REJETEE)
        self.assertEqual(rec.nouvelle_note, None)  # No note change on rejection

    def test_student_cannot_assign_reclamation(self):
        """Test: Student cannot assign (traiter) a reclamation - only coordinator can"""
        # Student creates a reclamation
        self.client.force_authenticate(user=self.etudiant)
        create_resp = self.client.post('/api/reclamations/create/', {
            'motif': 'ERREUR_SAISIE',
            'description': 'Test',
            'note_elementaire': self.note.id,
        })
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        reclamation_id = create_resp.data['id']

        # Student tries to assign - should be forbidden
        assign_resp = self.client.patch(f'/api/coordinator/reclamations/{reclamation_id}/traiter/')
        self.assertEqual(assign_resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_assign_non_pending_reclamation(self):
        """Test: Cannot assign a reclamation that is not EN_ATTENTE"""
        # Create a reclamation in EN_COURS status
        rec = make_reclamation(self.etudiant, self.note, StatutReclamation.EN_COURS)

        self.client.force_authenticate(user=self.coord)
        assign_resp = self.client.patch(f'/api/coordinator/reclamations/{rec.id}/traiter/')
        self.assertEqual(assign_resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_accept_without_commentaire(self):
        """Test: Cannot accept a reclamation without commentaire_decision"""
        rec = make_reclamation(self.etudiant, self.note, StatutReclamation.EN_COURS)

        self.client.force_authenticate(user=self.coord)
        accept_resp = self.client.post(f'/api/coordinator/reclamations/{rec.id}/accepter/', {
            'nouvelle_note': 15.00,
        })
        self.assertEqual(accept_resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_reject_without_commentaire(self):
        """Test: Cannot reject a reclamation without commentaire_decision"""
        rec = make_reclamation(self.etudiant, self.note, StatutReclamation.EN_COURS)

        self.client.force_authenticate(user=self.coord)
        reject_resp = self.client.post(f'/api/coordinator/reclamations/{rec.id}/rejeter/', {})
        self.assertEqual(reject_resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reclamation_detail_shows_historique(self):
        """Test: Reclamation detail includes status history"""
        rec = make_reclamation(self.etudiant, self.note)

        self.client.force_authenticate(user=self.etudiant)
        detail_resp = self.client.get(f'/api/reclamations/{rec.id}/')
        self.assertEqual(detail_resp.status_code, status.HTTP_200_OK)
        self.assertIn('historique_statuts', detail_resp.data)
        self.assertGreaterEqual(len(detail_resp.data['historique_statuts']), 1)

    def test_coordinator_can_view_all_reclamations(self):
        """Test: Coordinator can list all reclamations (not just their own)"""
        other = make_user('STUDENT002', Role.ETUDIANT)
        other_note = make_note(other)
        rec1 = make_reclamation(self.etudiant, self.note)
        rec2 = make_reclamation(other, other_note)

        self.client.force_authenticate(user=self.coord)
        list_resp = self.client.get('/api/coordinator/reclamations/')
        self.assertEqual(list_resp.status_code, status.HTTP_200_OK)
        # Coordinator should see both reclamations
        self.assertGreaterEqual(list_resp.data['count'], 2)

    def test_dashboard_stats(self):
        """Test: Dashboard returns correct statistics"""
        # Create reclamations in different states
        make_reclamation(self.etudiant, self.note, StatutReclamation.EN_ATTENTE)
        make_reclamation(self.etudiant, make_note(self.etudiant), StatutReclamation.EN_COURS)
        make_reclamation(self.etudiant, make_note(self.etudiant), StatutReclamation.ACCEPTEE)
        make_reclamation(self.etudiant, make_note(self.etudiant), StatutReclamation.REJETEE)

        self.client.force_authenticate(user=self.coord)
        dashboard_resp = self.client.get('/api/coordinator/dashboard/')
        self.assertEqual(dashboard_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(dashboard_resp.data['en_attente'], 1)
        self.assertEqual(dashboard_resp.data['en_cours'], 1)
        self.assertEqual(dashboard_resp.data['acceptee'], 1)
        self.assertEqual(dashboard_resp.data['rejetee'], 1)