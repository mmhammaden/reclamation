class NoteModel {
  final int id;
  final String codeModule;
  final String nomModule;
  final double noteContinu;
  final double noteFinal;
  final double valeurNote;
  final double? noteSur;
  final String semestre;
  final String anneeAcademique;
  final bool aReclamationActive;

  NoteModel({
    required this.id,
    required this.codeModule,
    required this.nomModule,
    this.noteContinu = 0.0,
    this.noteFinal = 0.0,
    required this.valeurNote,
    this.noteSur,
    required this.semestre,
    required this.anneeAcademique,
    this.aReclamationActive = false,
  });

  factory NoteModel.fromJson(Map<String, dynamic> json) {
    return NoteModel(
      id: json['id'] as int? ?? 0,
      codeModule: json['code_element'] as String? ?? json['code_module'] as String? ?? '',
      nomModule: json['nom_matiere'] as String? ?? json['nom_module'] as String? ?? '',
      noteContinu: _toDouble(json['note_continu']) ?? 0.0,
      noteFinal: _toDouble(json['note_final']) ?? 0.0,
      valeurNote: _toDouble(json['note_moyenne'] ?? json['valeur_note']) ?? 0.0,
      noteSur: _toDouble(json['note_sur']),
      semestre: json['semestre'] as String? ?? '',
      anneeAcademique: json['annee_academique'] as String? ?? '',
      aReclamationActive: json['a_reclamation_active'] as bool? ?? false,
    );
  }

  static double? _toDouble(dynamic value) {
    if (value == null) return null;
    if (value is num) return value.toDouble();
    return double.tryParse(value.toString());
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'code_element': codeModule,
      'nom_matiere': nomModule,
      'note_continu': noteContinu,
      'note_final': noteFinal,
      'note_moyenne': valeurNote,
      'note_sur': noteSur,
      'semestre': semestre,
      'annee_academique': anneeAcademique,
      'a_reclamation_active': aReclamationActive,
    };
  }
}
