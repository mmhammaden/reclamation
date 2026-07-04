import 'package:freezed_annotation/freezed_annotation.dart';

part 'note.freezed.dart';
part 'note.g.dart';

@freezed
class NoteElementaire with _$NoteElementaire {
  const factory NoteElementaire({
    required int id,
    required String codeModule,
    required String libelleModule,
    required double valeurNote,
    required double noteSur,
    required String semestre,
    required String anneeAcademique,
    required DateTime dateSaisie,
    required bool estVerifiee,
  }) = _NoteElementaire;

  factory NoteElementaire.fromJson(Map<String, dynamic> json) =>
      _$NoteElementaireFromJson(json);
}

@freezed
class NoteListResponse with _$NoteListResponse {
  const factory NoteListResponse({
    required int count,
    required String? next,
    required String? previous,
    required List<NoteElementaire> results,
  }) = _NoteListResponse;

  factory NoteListResponse.fromJson(Map<String, dynamic> json) =>
      _$NoteListResponseFromJson(json);
}