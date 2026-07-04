import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';
import 'package:reclamations_iscae/core/api/dio_client.dart';
import 'package:reclamations_iscae/core/models/user.dart';
import 'package:reclamations_iscae/core/storage/secure_storage.dart';

class AuthNotifier extends StateNotifier<AsyncValue<User?>> {
  final SecureStorage _secureStorage = SecureStorage.instance;
  
  AuthNotifier() : super(const AsyncValue.data(null)) {
    _loadUser();
  }

  Future<void> _loadUser() async {
    final userJson = await _secureStorage.getUser();
    if (userJson != null) {
      try {
        final userMap = jsonDecode(userJson) as Map<String, dynamic>;
        final userData = UserData.fromJson(userMap);
        
        // Convert UserData to User with role
        final user = User(
          id: userData.id,
          matricule: userData.matricule,
          email: userData.email,
          role: userData.role,
          firstName: userData.nom.split(' ').first,
          lastName: userData.nom.split(' ').skip(1).join(' '),
          telephone: '',
          isActive: true,
        );
        
        state = AsyncValue.data(user);
      } catch (e) {
        await _secureStorage.clearAll();
        state = const AsyncValue.data(null);
      }
    }
  }

  Future<void> login(LoginRequest request) async {
    state = const AsyncValue.loading();
    try {
      final response = await DioClient().dio.post(
        '/auth/login/',
        data: request.toJson(),
      );

      final loginResponse = LoginResponse.fromJson(response.data);
      await _secureStorage.saveAccessToken(loginResponse.access);
      await _secureStorage.saveRefreshToken(loginResponse.refresh);
      await _secureStorage.saveUser(jsonEncode(loginResponse.user.toJson()));

      // Convert UserData to User
      final user = User(
        id: loginResponse.user.id,
        matricule: loginResponse.user.matricule,
        email: loginResponse.user.email,
        role: loginResponse.user.role,
        firstName: loginResponse.user.nom.split(' ').first,
        lastName: loginResponse.user.nom.split(' ').skip(1).join(' '),
        telephone: '',
        isActive: true,
      );

      state = AsyncValue.data(user);
    } on DioException catch (e) {
      state = AsyncValue.error(e.message ?? 'Login failed', StackTrace.current);
    }
  }

  Future<void> logout() async {
    final refreshToken = await _secureStorage.getRefreshToken();
    if (refreshToken != null) {
      try {
        await DioClient().dio.post('/auth/logout/', data: {'refresh': refreshToken});
      } catch (_) {}
    }
    await _secureStorage.clearAll();
    state = const AsyncValue.data(null);
  }
}

final authProvider = StateNotifierProvider<AuthNotifier, AsyncValue<User?>>((ref) {
  return AuthNotifier();
});