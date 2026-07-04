import 'package:dio/dio.dart';
import 'package:reclamations_iscae/core/storage/secure_storage.dart';

class DioClient {
  static final DioClient _instance = DioClient._internal();
  factory DioClient() => _instance;

  late final Dio dio;

  DioClient._internal() {
    dio = Dio(BaseOptions(
      baseUrl: 'http://10.0.2.2:8000/api',
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ));

    dio.interceptors.add(AuthInterceptor());
  }
}

class AuthInterceptor extends Interceptor {
  final SecureStorage _secureStorage = SecureStorage();

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
          final dio = DioClient().dio;
          final refreshResponse = await dio.post(
            '/auth/refresh/',
            data: {'refresh': refreshToken},
          );

          final newAccessToken = refreshResponse.data['access'] as String;
          await _secureStorage.saveAccessToken(newAccessToken);

          final requestOptions = err.requestOptions;
          requestOptions.headers['Authorization'] = 'Bearer $newAccessToken';

          final response = await dio.fetch(requestOptions);
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