import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../core/network/dio_client.dart';
import '../core/network/connectivity_service.dart';
import '../core/storage/token_manager.dart';
import '../core/storage/cache_service.dart';
import '../models/note_model.dart';
import '../models/notification_model.dart';
import '../models/reclamation_model.dart';
import '../models/user_model.dart';
import '../services/auth_service.dart';
import '../services/note_service.dart';
import '../services/notification_service.dart';
import '../services/reclamation_service.dart';

// ─── Core Providers ──────────────────────────────────────────────────────────

final flutterSecureStorageProvider = Provider<FlutterSecureStorage>((ref) {
  return const FlutterSecureStorage();
});

final tokenManagerProvider = Provider<TokenManager>((ref) {
  final storage = ref.watch(flutterSecureStorageProvider);
  return TokenManager(storage: storage);
});

final connectivityServiceProvider = Provider<ConnectivityService>((ref) {
  final service = ConnectivityService();
  service.init();
  ref.onDispose(() => service.dispose());
  return service;
});

final dioClientProvider = Provider<DioClient>((ref) {
  final tokenManager = ref.watch(tokenManagerProvider);
  final connectivityService = ref.watch(connectivityServiceProvider);
  return DioClient(
    tokenManager: tokenManager,
    connectivityService: connectivityService,
  );
});

// ─── Service Providers ───────────────────────────────────────────────────────

final authServiceProvider = Provider<AuthService>((ref) {
  final dioClient = ref.watch(dioClientProvider);
  final tokenManager = ref.watch(tokenManagerProvider);
  return AuthService(dioClient: dioClient, tokenManager: tokenManager);
});

final noteServiceProvider = Provider<NoteService>((ref) {
  final dioClient = ref.watch(dioClientProvider);
  return NoteService(dioClient: dioClient);
});

final reclamationServiceProvider = Provider<ReclamationService>((ref) {
  final dioClient = ref.watch(dioClientProvider);
  return ReclamationService(dioClient: dioClient);
});

final notificationServiceProvider = Provider<NotificationService>((ref) {
  final dioClient = ref.watch(dioClientProvider);
  return NotificationService(dioClient: dioClient);
});

// ─── Auth State ──────────────────────────────────────────────────────────────

enum AuthStatus { unknown, authenticated, unauthenticated }

class AuthState {
  final AuthStatus status;
  final UserModel? user;
  final String? error;
  final bool isLoading;

  const AuthState({
    this.status = AuthStatus.unknown,
    this.user,
    this.error,
    this.isLoading = false,
  });

  AuthState copyWith({
    AuthStatus? status,
    UserModel? user,
    String? error,
    bool? isLoading,
  }) {
    return AuthState(
      status: status ?? this.status,
      user: user ?? this.user,
      error: error,
      isLoading: isLoading ?? this.isLoading,
    );
  }
}

class AuthNotifier extends Notifier<AuthState> {
  @override
  AuthState build() {
    _checkAuth();
    return const AuthState();
  }

  Future<void> _checkAuth() async {
    final authService = ref.read(authServiceProvider);
    try {
      final isLoggedIn = await authService.isLoggedIn();
      if (isLoggedIn) {
        final user = await authService.getCachedUser();
        if (user != null && user.isStudent) {
          state = AuthState(
            status: AuthStatus.authenticated,
            user: user,
          );
          return;
        }
      }
      state = const AuthState(status: AuthStatus.unauthenticated);
    } catch (_) {
      state = const AuthState(status: AuthStatus.unauthenticated);
    }
  }

  Future<void> login(String matricule, String password) async {
    final authService = ref.read(authServiceProvider);
    state = state.copyWith(isLoading: true, error: null);
    try {
      final user = await authService.login(matricule, password);
      if (!user.isStudent) {
        await authService.logout();
        state = state.copyWith(
          isLoading: false,
          error: 'Cette application est réservée aux étudiants.',
        );
        return;
      }
      state = AuthState(
        status: AuthStatus.authenticated,
        user: user,
      );
    } on DioException catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.message ?? 'Une erreur est survenue. Veuillez réessayer.',
      );
    } on Exception catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString().replaceFirst('Exception: ', ''),
      );
    }
  }

  Future<void> logout() async {
    final authService = ref.read(authServiceProvider);
    await authService.logout();
    await CacheService.clearAll();
    state = const AuthState(status: AuthStatus.unauthenticated);
  }

  void clearError() {
    state = state.copyWith(error: null);
  }

  Future<void> changePassword({
    required String oldPassword,
    required String newPassword,
  }) async {
    final authService = ref.read(authServiceProvider);
    state = state.copyWith(isLoading: true, error: null);
    try {
      await authService.changePassword(
        oldPassword: oldPassword,
        newPassword: newPassword,
      );
      state = state.copyWith(isLoading: false);
    } on DioException catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.message ?? 'Une erreur est survenue. Veuillez réessayer.',
      );
      rethrow;
    } on Exception catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString().replaceFirst('Exception: ', ''),
      );
      rethrow;
    }
  }
}

final authProvider = NotifierProvider<AuthNotifier, AuthState>(
  AuthNotifier.new,
);

// ─── Notes State ─────────────────────────────────────────────────────────────

class NotesState {
  final List<NoteModel> notes;
  final bool isLoading;
  final String? error;
  final bool isFromCache;

  const NotesState({
    this.notes = const [],
    this.isLoading = false,
    this.error,
    this.isFromCache = false,
  });

  NotesState copyWith({
    List<NoteModel>? notes,
    bool? isLoading,
    String? error,
    bool? isFromCache,
  }) {
    return NotesState(
      notes: notes ?? this.notes,
      isLoading: isLoading ?? this.isLoading,
      error: error,
      isFromCache: isFromCache ?? this.isFromCache,
    );
  }
}

class NotesNotifier extends Notifier<NotesState> {
  @override
  NotesState build() {
    return const NotesState();
  }

  Future<void> loadNotes() async {
    final noteService = ref.read(noteServiceProvider);
    state = state.copyWith(isLoading: true, error: null);

    // Load from cache first for instant display
    if (CacheService.hasCachedNotes()) {
      state = NotesState(
        notes: CacheService.getCachedNotes(),
        isFromCache: true,
      );
    }

    try {
      final notes = await noteService.getNotes();
      // Cache the fresh data
      await CacheService.cacheNotes(notes);
      state = NotesState(notes: notes);
    } on DioException catch (e) {
      // If we have cached data, keep showing it and just update error
      if (state.notes.isNotEmpty) {
        state = state.copyWith(
          isLoading: false,
          error: 'Mode hors-ligne: ${e.message ?? e.toString()}',
        );
      } else {
        state = state.copyWith(
          isLoading: false,
          error: e.message ?? 'Une erreur est survenue. Veuillez réessayer.',
        );
      }
    } on Exception catch (e) {
      // If we have cached data, keep showing it and just update error
      if (state.notes.isNotEmpty) {
        state = state.copyWith(
          isLoading: false,
          error: 'Mode hors-ligne: ${e.toString().replaceFirst("Exception: ", "")}',
        );
      } else {
        state = state.copyWith(
          isLoading: false,
          error: e.toString().replaceFirst('Exception: ', ''),
        );
      }
    }
  }
}

final notesProvider = NotifierProvider<NotesNotifier, NotesState>(
  NotesNotifier.new,
);

// ─── Reclamations State ──────────────────────────────────────────────────────

class ReclamationsState {
  final List<ReclamationModel> reclamations;
  final ReclamationModel? selectedReclamation;
  final bool isLoading;
  final bool isCreating;
  final double uploadProgress;
  final String? error;
  final bool isFromCache;

  const ReclamationsState({
    this.reclamations = const [],
    this.selectedReclamation,
    this.isLoading = false,
    this.isCreating = false,
    this.uploadProgress = 0,
    this.error,
    this.isFromCache = false,
  });

  ReclamationsState copyWith({
    List<ReclamationModel>? reclamations,
    ReclamationModel? selectedReclamation,
    bool? isLoading,
    bool? isCreating,
    double? uploadProgress,
    String? error,
    bool clearSelected = false,
    bool? isFromCache,
  }) {
    return ReclamationsState(
      reclamations: reclamations ?? this.reclamations,
      selectedReclamation:
          clearSelected ? null : (selectedReclamation ?? this.selectedReclamation),
      isLoading: isLoading ?? this.isLoading,
      isCreating: isCreating ?? this.isCreating,
      uploadProgress: uploadProgress ?? this.uploadProgress,
      error: error,
      isFromCache: isFromCache ?? this.isFromCache,
    );
  }
}

class ReclamationsNotifier extends Notifier<ReclamationsState> {
  @override
  ReclamationsState build() {
    return const ReclamationsState();
  }

  Future<void> loadReclamations() async {
    final reclamationService = ref.read(reclamationServiceProvider);
    state = state.copyWith(isLoading: true, error: null);

    // Load from cache first for instant display
    if (CacheService.hasCachedReclamations()) {
      state = ReclamationsState(
        reclamations: CacheService.getCachedReclamations(),
        isFromCache: true,
      );
    }

    try {
      final reclamations = await reclamationService.getReclamations();
      // Cache the fresh data
      await CacheService.cacheReclamations(reclamations);
      state = ReclamationsState(reclamations: reclamations);
    } on DioException catch (e) {
      // If we have cached data, keep showing it and just update error
      if (state.reclamations.isNotEmpty) {
        state = state.copyWith(
          isLoading: false,
          error: 'Mode hors-ligne: ${e.message ?? e.toString()}',
        );
      } else {
        state = state.copyWith(
          isLoading: false,
          error: e.message ?? 'Une erreur est survenue. Veuillez réessayer.',
        );
      }
    } on Exception catch (e) {
      // If we have cached data, keep showing it and just update error
      if (state.reclamations.isNotEmpty) {
        state = state.copyWith(
          isLoading: false,
          error: 'Mode hors-ligne: ${e.toString().replaceFirst("Exception: ", "")}',
        );
      } else {
        state = state.copyWith(
          isLoading: false,
          error: e.toString().replaceFirst('Exception: ', ''),
        );
      }
    }
  }

  Future<void> loadReclamationDetail(int id) async {
    final reclamationService = ref.read(reclamationServiceProvider);
    state = state.copyWith(isLoading: true, error: null);

    // Load from cache first
    final cached = CacheService.getCachedReclamationDetail(id);
    if (cached != null) {
      state = state.copyWith(
        selectedReclamation: cached,
        isLoading: false,
      );
    }

    try {
      final reclamation = await reclamationService.getReclamation(id);
      // Cache the fresh data
      await CacheService.cacheReclamationDetail(reclamation);
      state = state.copyWith(
        selectedReclamation: reclamation,
        isLoading: false,
      );
    } on DioException catch (e) {
      // If we already have cached detail, keep it
      if (state.selectedReclamation == null) {
        state = state.copyWith(
          isLoading: false,
          error: e.message ?? 'Une erreur est survenue. Veuillez réessayer.',
        );
      } else {
        state = state.copyWith(
          isLoading: false,
          error: 'Mode hors-ligne: ${e.message ?? e.toString()}',
        );
      }
    } on Exception catch (e) {
      // If we already have cached detail, keep it
      if (state.selectedReclamation == null) {
        state = state.copyWith(
          isLoading: false,
          error: e.toString().replaceFirst('Exception: ', ''),
        );
      } else {
        state = state.copyWith(
          isLoading: false,
          error: 'Mode hors-ligne: ${e.toString().replaceFirst("Exception: ", "")}',
        );
      }
    }
  }

  Future<void> createReclamation({
    required String motif,
    required int noteId,
    String? filePath,
  }) async {
    final reclamationService = ref.read(reclamationServiceProvider);
    state = state.copyWith(isCreating: true, error: null, uploadProgress: 0);
    try {
      final reclamation = await reclamationService.createReclamation(
        motif: motif,
        noteId: noteId,
        filePath: filePath,
        onUploadProgress: (sent, total) {
          if (total > 0) {
            state = state.copyWith(
              uploadProgress: sent / total,
            );
          }
        },
      );
      state = state.copyWith(
        reclamations: [reclamation, ...state.reclamations],
        isCreating: false,
        uploadProgress: 0,
      );
      // Update cache with new reclamation
      await CacheService.cacheReclamations(state.reclamations);
    } on DioException catch (e) {
      state = state.copyWith(
        isCreating: false,
        uploadProgress: 0,
        error: e.message ?? 'Une erreur est survenue. Veuillez réessayer.',
      );
      rethrow;
    } on Exception catch (e) {
      state = state.copyWith(
        isCreating: false,
        uploadProgress: 0,
        error: e.toString().replaceFirst('Exception: ', ''),
      );
      rethrow;
    }
  }

  Future<void> deleteReclamation(int id) async {
    final reclamationService = ref.read(reclamationServiceProvider);
    try {
      await reclamationService.deleteReclamation(id);
      state = state.copyWith(
        reclamations: state.reclamations.where((r) => r.id != id).toList(),
      );
      // Update cache after deletion
      await CacheService.cacheReclamations(state.reclamations);
    } on DioException catch (e) {
      state = state.copyWith(error: e.message ?? 'Une erreur est survenue. Veuillez réessayer.');
    } on Exception catch (e) {
      state = state.copyWith(error: e.toString().replaceFirst('Exception: ', ''));
    }
  }
}

final reclamationsProvider = NotifierProvider<ReclamationsNotifier, ReclamationsState>(
  ReclamationsNotifier.new,
);

// ─── Notifications State ─────────────────────────────────────────────────────

class NotificationsState {
  final List<NotificationModel> notifications;
  final int unreadCount;
  final bool isLoading;
  final String? error;

  const NotificationsState({
    this.notifications = const [],
    this.unreadCount = 0,
    this.isLoading = false,
    this.error,
  });

  NotificationsState copyWith({
    List<NotificationModel>? notifications,
    int? unreadCount,
    bool? isLoading,
    String? error,
  }) {
    return NotificationsState(
      notifications: notifications ?? this.notifications,
      unreadCount: unreadCount ?? this.unreadCount,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

class NotificationsNotifier extends Notifier<NotificationsState> {
  @override
  NotificationsState build() {
    return const NotificationsState();
  }

  Future<void> loadNotifications() async {
    final notificationService = ref.read(notificationServiceProvider);
    state = state.copyWith(isLoading: true, error: null);
    try {
      final notifications = await notificationService.getNotifications();
      final unreadCount = await notificationService.getUnreadCount();
      state = NotificationsState(
        notifications: notifications,
        unreadCount: unreadCount,
      );
    } on DioException catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.message ?? 'Une erreur est survenue. Veuillez réessayer.',
      );
    } on Exception catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString().replaceFirst('Exception: ', ''),
      );
    }
  }

  Future<void> markAsRead(int id) async {
    final notificationService = ref.read(notificationServiceProvider);
    try {
      await notificationService.markAsRead(id);
      state = state.copyWith(
        notifications: state.notifications.map((n) {
          if (n.id == id) {
            return NotificationModel(
              id: n.id,
              contenu: n.contenu,
              estLu: true,
              type: n.type,
              dateCreation: n.dateCreation,
              reclamation: n.reclamation,
            );
          }
          return n;
        }).toList(),
        unreadCount: state.unreadCount > 0 ? state.unreadCount - 1 : 0,
      );
    } catch (_) {}
  }

  Future<void> markAllAsRead() async {
    final notificationService = ref.read(notificationServiceProvider);
    try {
      await notificationService.markAllAsRead();
      state = state.copyWith(
        notifications: state.notifications
            .map((n) => NotificationModel(
                  id: n.id,
                  contenu: n.contenu,
                  estLu: true,
                  type: n.type,
                  dateCreation: n.dateCreation,
                  reclamation: n.reclamation,
                ))
            .toList(),
        unreadCount: 0,
      );
    } catch (_) {}
  }
}

final notificationsProvider = NotifierProvider<NotificationsNotifier, NotificationsState>(
  NotificationsNotifier.new,
);