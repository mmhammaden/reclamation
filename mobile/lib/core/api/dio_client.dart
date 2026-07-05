import 'package:dio/dio.dart';
import 'package:reclamations_iscae/core/storage/secure_storage.dart';
import 'api_config.dart';

// Additional Dio import for creating separate instance in interceptor
import 'dart:async';

class DioClient {
  static final DioClient _instance = DioClient._internal();
  factory DioClient() => _instance;

  late final Dio dio;

  DioClient._internal() {
    dio = Dio(BaseOptions(
      baseUrl: ApiConfig.baseUrl,
      connectTimeout: const Duration(seconds: ApiConfig.connectTimeoutSeconds),
      receiveTimeout: const Duration(seconds: ApiConfig.receiveTimeoutSeconds),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ));

    dio.interceptors.add(AuthInterceptor());
  }
}

class AuthInterceptor extends Interceptor {
  final SecureStorage _secureStorage = SecureStorage.instance;

  @override
  void onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    final token = await _secureStorage.getAccessToken();
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }

  @override
  void onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    if (err.response?.statusCode == 401) {
      final refreshToken = await _secureStorage.getRefreshToken();
      if (refreshToken != null) {
        try {
          // Use a separate Dio instance without interceptors to avoid infinite loop
          final refreshDio = Dio();
          refreshDio.options.baseUrl = 'http://10.0.2.2:8000/api';
          refreshDio.options.connectTimeout = const Duration(seconds: 30);
          refreshDio.options.receiveTimeout = const Duration(seconds: 30);
          
          final refreshResponse = await refreshDio.post(
            '/auth/refresh/',
            data: {'refresh': refreshToken},
          );

          final newAccessToken = refreshResponse.data['access'] as String;
          await _secureStorage.saveAccessToken(newAccessToken);

          final requestOptions = err.requestOptions;
          requestOptions.headers['Authorization'] = 'Bearer $newAccessToken';

          final response = await DioClient().dio.fetch(requestOptions);
          handler.resolve(response);
          return;
        } on DioException catch (e) {
          if (e.response?.statusCode == 401) {
            await _secureStorage.clearAll();
          }
        }
      } else {
        await _secureStorage.clearAll();
      }
    }
    handler.next(err);
  }
}
