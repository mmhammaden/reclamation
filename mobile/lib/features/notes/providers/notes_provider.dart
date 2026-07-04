import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';
import 'package:reclamations_iscae/core/api/dio_client.dart';
import 'package:reclamations_iscae/core/models/note.dart';

class NotesNotifier extends StateNotifier<AsyncValue<NoteListResponse?>> {
  NotesNotifier() : super(const AsyncValue.data(null)) {
    loadNotes();
  }

  Future<void> loadNotes({int page = 1}) async {
    state = const AsyncValue.loading();
    try {
      final response = await DioClient().dio.get(
        '/notes/',
        queryParameters: {'page': page},
      );
      state = AsyncValue.data(NoteListResponse.fromJson(response.data));
    } on DioException catch (e) {
      state = AsyncValue.error(e.message ?? 'Failed to load notes', StackTrace.current);
    }
  }
}

final notesProvider = StateNotifierProvider<NotesNotifier, AsyncValue<NoteListResponse?>>((ref) {
  return NotesNotifier();
});