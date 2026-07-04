import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:dio/dio.dart';
import 'package:reclamations_iscae/core/api/dio_client.dart';
import 'package:reclamations_iscae/core/models/notification.dart';

class NotificationsNotifier extends StateNotifier<AsyncValue<List<Notification>>> {
  NotificationsNotifier() : super(const AsyncValue.data([])) {
    _initNotifications();
  }

  Future<void> _initNotifications() async {
    try {
      // Request permission for iOS
      final settings = await FirebaseMessaging.instance.requestPermission(
        alert: true,
        badge: true,
        sound: true,
      );

      if (settings.authorizationStatus == AuthorizationStatus.authorized) {
        // Get FCM token
        final token = await FirebaseMessaging.instance.getToken();
        if (token != null) {
          // Detect platform
          String platform;
          if (kIsWeb) {
            platform = 'web';
          } else if (Platform.isAndroid) {
            platform = 'android';
          } else if (Platform.isIOS) {
            platform = 'ios';
          } else {
            platform = 'unknown';
          }

          // Send token to backend
          await DioClient().dio.post('/notifications/register-token/', data: {
            'token': token,
            'platform': platform,
          });
        }

        // Listen for foreground messages
        FirebaseMessaging.onMessage.listen((RemoteMessage message) {
          // Show in-app notification
          if (message.notification != null) {
            final newNotification = Notification(
              id: DateTime.now().millisecondsSinceEpoch,
              contenu: message.notification!.body ?? '',
              estLu: false,
              typeNotification: 'push',
              createdAt: DateTime.now(),
              reclamationId: null,
            );
            state.whenOrNull(
              data: (notifications) {
                state = AsyncValue.data([newNotification, ...notifications]);
              },
            );
          }
        });
      }
    } catch (e) {
      if (kDebugMode) {
        print('FCM initialization error: $e');
      }
    }
  }

  Future<void> loadNotifications() async {
    state = const AsyncValue.loading();
    try {
      final response = await DioClient().dio.get('/notifications/');
      final notifications = (response.data as List)
          .map((e) => Notification.fromJson(e))
          .toList();
      state = AsyncValue.data(notifications);
    } on DioException catch (e) {
      state = AsyncValue.error(e.message ?? 'Failed to load notifications', StackTrace.current);
    }
  }
}

final notificationsProvider = StateNotifierProvider<NotificationsNotifier, AsyncValue<List<Notification>>>((ref) {
  return NotificationsNotifier();
});