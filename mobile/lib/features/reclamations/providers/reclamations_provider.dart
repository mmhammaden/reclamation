import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';
import 'package:reclamations_iscae/core/api/dio_client.dart';
import 'package:reclamations_iscae/core/models/reclamation.dart';

class ReclamationsNotifier extends StateNotifier<AsyncValue<List<ReclamationListItem>>> {
  ReclamationsNotifier() : super(const AsyncValue.data([])) {
    loadReclamations();
  }

  Future<void> loadReclamations({int page = 1}) async {
    state = const AsyncValue.loading();
    try {
      final response = await DioClient().dio.get(
        '/reclamations/',
        queryParameters: {'page': page},
      );
      final reclamations = (response.data['results'] as List)
          .map((e) => ReclamationListItem.fromJson(e))
          .toList();
      state = AsyncValue.data(reclamations);
    } on DioException catch (e) {
      state = AsyncValue.error(e.message ?? 'Failed to load reclamations', StackTrace.current);
    }
  }

  Future<void> loadMore() async {
    // Pagination support - load next page
    // Note: This requires tracking current page in state
    // For now, this is a placeholder for future implementation
    // The current implementation only loads page 1
  }

  Future<void> createReclamation(ReclamationCreate request) async {
    try {
      final formData = FormData.fromMap({
        'motif': request.motif.name,
        'description': request.description,
        'note_elementaire': request.noteElementaire,
      });

      await DioClient().dio.post('/reclamations/create/', data: formData);
      await loadReclamations();
    } on DioException catch (e) {
      throw Exception(e.message ?? 'Failed to create reclamation');
    }
  }

  Future<void> deleteReclamation(int id) async {
    try {
      await DioClient().dio.delete('/reclamations/$id/delete/');
      state.whenOrNull(
        data: (reclamations) {
          state = AsyncValue.data(reclamations.where((r) => r.id != id).toList());
        },
      );
    } on DioException catch (e) {
      throw Exception(e.message ?? 'Failed to delete reclamation');
    }
  }
}

final reclamationsProvider = StateNotifierProvider<ReclamationsNotifier, AsyncValue<List<ReclamationListItem>>>((ref) {
  return ReclamationsNotifier();
});