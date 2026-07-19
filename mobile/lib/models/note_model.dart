class NoteModel {
  final int id;
  final String codeModule;
  final String nomModule;
  final double valeurNote;
  final double? noteSur;
  final String semestre;
  final String anneeAcademique;
  final bool aReclamationActive;

  NoteModel({
    required this.id,
    required this.codeModule,
    required this.nomModule,
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
      valeurNote: (json['note_moyenne'] as num?)?.toDouble() ?? (json['valeur_note'] as num?)?.toDouble() ?? 0.0,
      noteSur: (json['note_sur'] as num?)?.toDouble(),
      semestre: json['semestre'] as String? ?? '',
      anneeAcademique: json['annee_academique'] as String? ?? '',
      aReclamationActive: json['a_reclamation_active'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'code_element': codeModule,
      'nom_matiere': nomModule,
      'note_moyenne': valeurNote,
      'note_sur': noteSur,
      'semestre': semestre,
      'annee_academique': anneeAcademique,
      'a_reclamation_active': aReclamationActive,
    };
  }
}