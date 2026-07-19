import '../core/constants/api_constants.dart';
import '../core/network/dio_client.dart';
import '../models/note_model.dart';

class NoteService {
  final DioClient _dioClient;

  NoteService({required DioClient dioClient}) : _dioClient = dioClient;

  /// Get all notes for the current student
  /// The API returns ResultatSemestre objects with nested elements,
  /// we flatten them into individual NoteModel objects
  Future<List<NoteModel>> getNotes() async {
    final response = await _dioClient.get(ApiConstants.notes);
    final data = response.data as List<dynamic>;
    
    final List<NoteModel> notes = [];
    for (final semesterData in data) {
      final semester = semesterData as Map<String, dynamic>;
      final semestre = semester['semestre'] as String? ?? '';
      final anneeAcademique = semester['annee_academique'] as String? ?? '';
      final elements = semester['elements'] as List<dynamic>? ?? [];
      
      for (final elementData in elements) {
        final element = elementData as Map<String, dynamic>;
        // Create NoteModel from element data, adding semester info
        notes.add(NoteModel(
          id: element['id'] as int? ?? 0,
          codeModule: element['code_element'] as String? ?? '',
          nomModule: element['nom_matiere'] as String? ?? '',
          valeurNote: (element['note_moyenne'] as num?)?.toDouble() ?? 0.0,
          noteSur: null, // The API doesn't provide note_sur, it's always /20
          semestre: semestre,
          anneeAcademique: anneeAcademique,
          aReclamationActive: element['a_reclamation_active'] as bool? ?? false,
        ));
      }
    }
    
    return notes;
  }

  /// Get a single note by ID
  Future<NoteModel> getNote(int id) async {
    final response = await _dioClient.get('${ApiConstants.notes}$id/');
    final data = response.data as Map<String, dynamic>;
    final semestre = data['semestre'] as String? ?? '';
    final anneeAcademique = data['annee_academique'] as String? ?? '';
    final elements = data['elements'] as List<dynamic>? ?? [];
    
    // Find the element with matching id
    for (final elementData in elements) {
      final element = elementData as Map<String, dynamic>;
      if (element['id'] == id) {
        return NoteModel(
          id: element['id'] as int,
          codeModule: element['code_element'] as String? ?? '',
          nomModule: element['nom_matiere'] as String? ?? '',
          valeurNote: (element['note_moyenne'] as num?)?.toDouble() ?? 0.0,
          noteSur: null,
          semestre: semestre,
          anneeAcademique: anneeAcademique,
          aReclamationActive: element['a_reclamation_active'] as bool? ?? false,
        );
      }
    }
    
    // Fallback: return a basic note if element not found
    return NoteModel(
      id: id,
      codeModule: '',
      nomModule: '',
      valeurNote: 0.0,
      semestre: semestre,
      anneeAcademique: anneeAcademique,
    );
  }
}