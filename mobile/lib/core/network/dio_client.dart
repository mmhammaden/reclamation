import 'package:dio/dio.dart';
import '../constants/api_constants.dart';
import '../storage/token_manager.dart';
import 'connectivity_service.dart';

/// Centralized Dio HTTP client with JWT interceptor.
/// - Automatically attaches access token to requests
/// - Refreshes token on 401 responses
/// - Centralized error handling via onError interceptor
/// - Maps HTTP codes to user-friendly messages
/// - Connectivity check before requests
/// - Fallback URL support if primary URL fails
class DioClient {
  late final Dio _dio;
  final TokenManager _tokenManager;
  final ConnectivityService _connectivityService;
  String _currentBaseUrl;

  DioClient({
    required TokenManager tokenManager,
    ConnectivityService? connectivityService,
  })  : _tokenManager = tokenManager,
        _connectivityService = connectivityService ?? ConnectivityService(),
        _currentBaseUrl = ApiConstants.baseUrl {
    _dio = Dio(
      BaseOptions(
        baseUrl: _currentBaseUrl,
        connectTimeout: ApiConstants.connectTimeout,
        receiveTimeout: ApiConstants.receiveTimeout,
        sendTimeout: ApiConstants.sendTimeout,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );

    _dio.interceptors.add(_createAuthInterceptor());
    _dio.interceptors.add(_createErrorInterceptor());
    _dio.interceptors.add(_createConnectivityInterceptor());
  }

  Dio get dio => _dio;
  String get currentBaseUrl => _currentBaseUrl;

  /// Try to find a working base URL by testing fallback URLs.
  /// Returns true if a working URL was found.
  Future<bool> tryFallbackUrls() async {
    final urlsToTry = <String>{};
    urlsToTry.add(ApiConstants.baseUrl);
    urlsToTry.addAll(ApiConstants.fallbackUrls);

    for (final url in urlsToTry) {
      if (url == _currentBaseUrl) continue;
      try {
        final testDio = Dio(BaseOptions(
          baseUrl: url,
          connectTimeout: const Duration(seconds: 5),
          receiveTimeout: const Duration(seconds: 5),
        ));
        await testDio.get(ApiConstants.healthCheck);
        // If we get here, the URL works
        _currentBaseUrl = url;
        _dio.options.baseUrl = url;
        return true;
      } catch (_) {
        continue;
      }
    }
    return false;
  }

  /// Create the connectivity interceptor that checks network before requests
  Interceptor _createConnectivityInterceptor() {
    return InterceptorsWrapper(
      onRequest: (options, handler) async {
        final isOnline = await _connectivityService.checkConnectivity();
        if (!isOnline) {
          handler.reject(
            DioException(
              requestOptions: options,
              type: DioExceptionType.connectionError,
              error: 'Aucune connexion internet. Veuillez vérifier votre réseau.',
              message: 'Aucune connexion internet. Veuillez vérifier votre réseau.',
            ),
          );
          return;
        }
        handler.next(options);
      },
    );
  }

  /// Create the auth interceptor that attaches JWT and handles refresh
  Interceptor _createAuthInterceptor() {
    return InterceptorsWrapper(
      onRequest: (options, handler) async {
        // Skip auth header for login and refresh endpoints
        if (!options.path.contains('/auth/login/') &&
            !options.path.contains('/auth/refresh/')) {
          final token = await _tokenManager.getAccessToken();
          if (token != null && token.isNotEmpty) {
            options.headers['Authorization'] = 'Bearer $token';
          }
        }
        handler.next(options);
      },
      onError: (error, handler) async {
        // If 401 Unauthorized, try to refresh the token
        if (error.response?.statusCode == 401) {
          final refreshToken = await _tokenManager.getRefreshToken();
          if (refreshToken != null && refreshToken.isNotEmpty) {
            try {
              // Attempt to refresh using a temporary Dio instance to avoid
              // recursive interceptor calls
              final tempDio = Dio(
                BaseOptions(
                  baseUrl: _currentBaseUrl,
                  connectTimeout: ApiConstants.connectTimeout,
                  receiveTimeout: ApiConstants.receiveTimeout,
                ),
              );
              final response = await tempDio.post(
                ApiConstants.refresh,
                data: {'refresh': refreshToken},
              );

              if (response.statusCode == 200) {
                final newAccessToken = response.data['access'] as String;
                await _tokenManager.saveAccessToken(newAccessToken);

                // Retry the original request with new token
                error.requestOptions.headers['Authorization'] =
                    'Bearer $newAccessToken';
                final retryResponse = await _dio.fetch(error.requestOptions);
                handler.resolve(retryResponse);
                return;
              }
            } catch (_) {
              // Refresh failed - force logout
              await _tokenManager.clearAll();
              handler.next(error);
              return;
            }
          }
        }
        handler.next(error);
      },
    );
  }

  /// Centralized error interceptor that maps HTTP codes to user-friendly messages
  Interceptor _createErrorInterceptor() {
    return InterceptorsWrapper(
      onError: (error, handler) {
        // Debug: Print the raw response data
        // ignore: avoid_print
        print('=== DIO ERROR ===');
        // ignore: avoid_print
        print('Status: ${error.response?.statusCode}');
        // ignore: avoid_print
        print('Data: ${error.response?.data}');
        // ignore: avoid_print
        print('Path: ${error.requestOptions.path}');
        // ignore: avoid_print
        print('Sent Data: ${error.requestOptions.data}');

        // Try to extract a specific error message from the backend response first
        String? userMessage;
        final responseData = error.response?.data;
        if (responseData is Map<String, dynamic>) {
          // Check for 'detail' field (DRF default)
          if (responseData.containsKey('detail')) {
            userMessage = responseData['detail'] as String?;
          }
          // Check for 'non_field_errors' (DRF serializer validation errors)
          else if (responseData.containsKey('non_field_errors')) {
            final nonFieldErrors = responseData['non_field_errors'];
            if (nonFieldErrors is List && nonFieldErrors.isNotEmpty) {
              userMessage = nonFieldErrors.first as String?;
            }
          } else {
            // Check for field-level errors like {"matricule": ["..."]}
            // Take the first error message from the first field
            for (final entry in responseData.entries) {
              final value = entry.value;
              if (value is List && value.isNotEmpty) {
                userMessage = value.first as String?;
                break;
              } else if (value is String) {
                userMessage = value;
                break;
              }
            }
          }
        }

        // Fallback to generic messages if no specific error was extracted
        if (userMessage == null || userMessage.isEmpty) {
          switch (error.response?.statusCode) {
            case 400:
              userMessage = 'Données invalides. Veuillez vérifier votre saisie.';
              break;
            case 401:
              userMessage = 'Session expirée. Veuillez vous reconnecter.';
              break;
            case 403:
              userMessage = 'Accès refusé. Vous n\'avez pas les permissions nécessaires.';
              break;
            case 404:
              userMessage = 'Ressource introuvable.';
              break;
            case 409:
              userMessage = 'Conflit : une réclamation existe déjà pour cette note.';
              break;
            case 422:
              userMessage = 'Données invalides.';
              break;
            case 429:
              userMessage = 'Trop de requêtes. Veuillez réessayer plus tard.';
              break;
            case 500:
              userMessage = 'Erreur serveur. Veuillez réessayer plus tard.';
              break;
            case 502:
              userMessage = 'Service temporairement indisponible.';
              break;
            case 503:
              userMessage = 'Service en maintenance. Réessayez plus tard.';
              break;
            default:
              if (error.type == DioExceptionType.connectionTimeout ||
                  error.type == DioExceptionType.receiveTimeout) {
                userMessage = 'Connexion au serveur impossible. Vérifiez votre connexion internet.';
              } else if (error.type == DioExceptionType.connectionError) {
                userMessage = 'Aucune connexion internet. Veuillez vérifier votre réseau.';
              } else {
                userMessage = 'Une erreur est survenue. Veuillez réessayer.';
              }
          }
        }

        // Attach user-friendly message to error for UI consumption
        error = DioException(
          requestOptions: error.requestOptions,
          response: error.response,
          type: error.type,
          error: error.error,
          message: userMessage!,
        );
        handler.next(error);
      },
    );
  }

  // Convenience methods
  Future<Response> get(
    String path, {
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) {
    return _dio.get(
      path,
      queryParameters: queryParameters,
      options: options,
      cancelToken: cancelToken,
    );
  }

  Future<Response> post(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) {
    return _dio.post(
      path,
      data: data,
      queryParameters: queryParameters,
      options: options,
      cancelToken: cancelToken,
    );
  }

  Future<Response> patch(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) {
    return _dio.patch(
      path,
      data: data,
      queryParameters: queryParameters,
      options: options,
      cancelToken: cancelToken,
    );
  }

  Future<Response> delete(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) {
    return _dio.delete(
      path,
      data: data,
      queryParameters: queryParameters,
      options: options,
      cancelToken: cancelToken,
    );
  }

  Future<void> refreshAccessToken(String refreshToken) async {
    final response = await post(
      ApiConstants.refresh,
      data: {'refresh': refreshToken},
    );
    final newAccessToken = response.data['access'] as String;
    await _tokenManager.saveAccessToken(newAccessToken);
  }

  Future<Response> uploadFile(
    String path, {
    required String filePath,
    String fileFieldName = 'fichier',
    Map<String, dynamic>? extraFields,
    void Function(int, int)? onSendProgress,
    CancelToken? cancelToken,
  }) async {
    final formData = FormData.fromMap({
      fileFieldName: await MultipartFile.fromFile(
        filePath,
        filename: filePath.split('/').last,
      ),
      if (extraFields != null) ...extraFields,
    });

    return _dio.post(
      path,
      data: formData,
      options: Options(
        headers: {'Content-Type': 'multipart/form-data'},
        sendTimeout: const Duration(seconds: 60), // Longer timeout for uploads
      ),
      onSendProgress: onSendProgress,
      cancelToken: cancelToken,
    );
  }
}