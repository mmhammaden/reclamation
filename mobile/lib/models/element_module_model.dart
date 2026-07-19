class ElementModuleModel {
  final int id;
  final String codeElement;
  final String nomMatiere;
  final double noteContinu;
  final double noteFinal;
  final double noteMoyenne;
  final double credit;
  final String observation;
  final String semestre;
  final String anneeAcademique;
  final bool aReclamationActive;

  ElementModuleModel({
    required this.id,
    required this.codeElement,
    required this.nomMatiere,
    required this.noteContinu,
    required this.noteFinal,
    required this.noteMoyenne,
    required this.credit,
    required this.observation,
    required this.semestre,
    required this.anneeAcademique,
    this.aReclamationActive = false,
  });

  factory ElementModuleModel.fromJson(Map<String, dynamic> json) {
    return ElementModuleModel(
      id: json['id'] as int? ?? 0,
      codeElement: json['code_element'] as String? ?? '',
      nomMatiere: json['nom_matiere'] as String? ?? '',
      noteContinu: (json['note_continu'] as num?)?.toDouble() ?? 0.0,
      noteFinal: (json['note_final'] as num?)?.toDouble() ?? 0.0,
      noteMoyenne: (json['note_moyenne'] as num?)?.toDouble() ?? 0.0,
      credit: (json['credit'] as num?)?.toDouble() ?? 0.0,
      observation: json['observation'] as String? ?? '',
      semestre: json['semestre'] as String? ?? '',
      anneeAcademique: json['annee_academique'] as String? ?? '',
      aReclamationActive: json['a_reclamation_active'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'code_element': codeElement,
      'nom_matiere': nomMatiere,
      'note_continu': noteContinu,
      'note_final': noteFinal,
      'note_moyenne': noteMoyenne,
      'credit': credit,
      'observation': observation,
      'semestre': semestre,
      'annee_academique': anneeAcademique,
      'a_reclamation_active': aReclamationActive,
    };
  }
}