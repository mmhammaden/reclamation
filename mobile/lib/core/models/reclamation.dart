import 'package:freezed_annotation/freezed_annotation.dart';

part 'reclamation.freezed.dart';
part 'reclamation.g.dart';

enum StatutReclamation {
  EN_ATTENTE,
  EN_COURS,
  ACCEPTEE,
  REJETEE,
  ARCHIVEE,
}

enum MotifReclamation {
  ERREUR_SAISIE,
  OUBLI_NOTE,
  VERIFICATION_COPIE,
  AUTRE,
}

@freezed
class ReclamationListItem with _$ReclamationListItem {
  const factory ReclamationListItem({
    required int id,
    required MotifReclamation motif,
    required StatutReclamation statut,
    required DateTime dateCreation,
    required DateTime dateLimiteTraitement,
    required String etudiantMatricule,
    required String etudiantNom,
    required String codeModule,
    required bool estEnRetard,
  }) = _ReclamationListItem;

  factory ReclamationListItem.fromJson(Map<String, dynamic> json) =>
      _$ReclamationListItemFromJson(json);
}

@freezed
class ReclamationDetail with _$ReclamationDetail {
  const factory ReclamationDetail({
    required int id,
    required MotifReclamation motif,
    required StatutReclamation statut,
    required String description,
    required String commentaireDecision,
    required int etudiant,
    required EtudiantInfo etudiantInfo,
    required int noteElementaire,
    required int? coordonnateur,
    required DateTime dateCreation,
    required DateTime dateLimiteTraitement,
    required DateTime? dateTraitement,
    required double? noteOriginale,
    required double? nouvelleNote,
    required List<PieceJointe> piecesJointes,
    required List<HistoriqueStatut> historiqueStatuts,
    required bool estEnRetard,
  }) = _ReclamationDetail;

  factory ReclamationDetail.fromJson(Map<String, dynamic> json) =>
      _$ReclamationDetailFromJson(json);
}

@freezed
class EtudiantInfo with _$EtudiantInfo {
  const factory EtudiantInfo({
    required String matricule,
    required String nom,
    required String email,
  }) = _EtudiantInfo;

  factory EtudiantInfo.fromJson(Map<String, dynamic> json) =>
      _$EtudiantInfoFromJson(json);
}

@freezed
class PieceJointe with _$PieceJointe {
  const factory PieceJointe({
    required int id,
    required String fichier,
    required String nomFichier,
    required int taille,
    required DateTime dateAjout,
  }) = _PieceJointe;

  factory PieceJointe.fromJson(Map<String, dynamic> json) =>
      _$PieceJointeFromJson(json);
}

@freezed
class HistoriqueStatut with _$HistoriqueStatut {
  const factory HistoriqueStatut({
    required int id,
    required String? statutPrecedent,
    required String nouveauStatut,
    required String commentaire,
    required int modifiePar,
    required String modifieParNom,
    required DateTime dateModification,
  }) = _HistoriqueStatut;

  factory HistoriqueStatut.fromJson(Map<String, dynamic> json) =>
      _$HistoriqueStatutFromJson(json);
}

@freezed
class ReclamationCreate with _$ReclamationCreate {
  const factory ReclamationCreate({
    required MotifReclamation motif,
    required String description,
    required int noteElementaire,
    List<String>? piecesJointes,
  }) = _ReclamationCreate;

  factory ReclamationCreate.fromJson(Map<String, dynamic> json) =>
      _$ReclamationCreateFromJson(json);
}

@freezed
class ReclamationDecision with _$ReclamationDecision {
  const factory ReclamationDecision({
    required String commentaireDecision,
    double? nouvelleNote,
  }) = _ReclamationDecision;

  factory ReclamationDecision.fromJson(Map<String, dynamic> json) =>
      _$ReclamationDecisionFromJson(json);
}