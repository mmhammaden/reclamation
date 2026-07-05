import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';
import 'package:reclamations_iscae/core/api/dio_client.dart';
import 'package:reclamations_iscae/core/models/reclamation.dart';

class ReclamationDetailNotifier extends StateNotifier<AsyncValue<ReclamationDetail?>> {
  ReclamationDetailNotifier() : super(const AsyncValue.data(null));

  Future<void> loadReclamation(int id) async {
    state = const AsyncValue.loading();
    try {
      final response = await DioClient().dio.get('/reclamations/$id/');
      state = AsyncValue.data(ReclamationDetail.fromJson(response.data));
    } on DioException catch (e) {
      state = AsyncValue.error(e.message ?? 'Failed to load reclamation', StackTrace.current);
    }
  }
}

// Use family provider to create separate instances for each reclamation ID
final reclamationDetailProvider = StateNotifierProvider.family<ReclamationDetailNotifier, AsyncValue<ReclamationDetail?>, int>((ref, id) {
  return ReclamationDetailNotifier();
});
