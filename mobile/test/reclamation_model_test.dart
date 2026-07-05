import 'package:flutter_test/flutter_test.dart';
import 'package:reclamations_iscae/core/models/reclamation.dart';

void main() {
  group('ReclamationListItem.fromJson', () {
    test('parses all fields correctly', () {
      final item = ReclamationListItem.fromJson({
        'id': 42,
        'motif': 'ERREUR_SAISIE',
        'statut': 'EN_ATTENTE',
        'date_creation': '2024-01-01T10:00:00Z',
        'date_limite_traitement': '2024-01-04T10:00:00Z',
        'etudiant_matricule': 'E001',
        'etudiant_nom': 'Ali Ben',
        'code_module': 'INF-101',
        'est_en_retard': false,
      });
      expect(item.id, 42);
      expect(item.motif, MotifReclamation.ERREUR_SAISIE);
      expect(item.statut, StatutReclamation.EN_ATTENTE);
      expect(item.estEnRetard, false);
    });
  });

  group('ReclamationCreate.toJson', () {
    test('serializes motif as string name', () {
      final create = ReclamationCreate(
        motif: MotifReclamation.OUBLI_NOTE,
        description: 'Note manquante',
        noteElementaire: 5,
      );
      final json = create.toJson();
      expect(json['description'], 'Note manquante');
      expect(json['note_elementaire'], 5);
    });
  });
}