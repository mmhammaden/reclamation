import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:reclamations_iscae/core/models/user.dart';

void main() {
  group('LoginRequest', () {
    test('toJson serializes correctly', () {
      final req = LoginRequest(matricule: 'E001', password: 'pass');
      final json = req.toJson();
      expect(json['matricule'], 'E001');
      expect(json['password'], 'pass');
    });
  });

  group('UserData.fromJson', () {
    test('parses valid json', () {
      final data = UserData.fromJson({
        'id': 1,
        'matricule': 'E001',
        'email': 'e@iscae.ma',
        'role': 'ETUDIANT',
        'nom': 'Ali Ben',
      });
      expect(data.matricule, 'E001');
      expect(data.role, Role.ETUDIANT);
      expect(data.nom, 'Ali Ben');
    });
  });
}