import 'package:flutter/foundation.dart';

/// Log ra console khi chạy `flutter run` — dùng tag để lọc nhanh.
class AppLogger {
  static void d(String tag, String message) {
    debugPrint('[$tag] $message');
  }

  static void i(String tag, String message) {
    debugPrint('[INFO][$tag] $message');
  }

  static void w(String tag, String message) {
    debugPrint('[WARN][$tag] $message');
  }

  static void e(String tag, String message, [Object? error, StackTrace? stackTrace]) {
    debugPrint('[ERROR][$tag] $message${error != null ? ' | $error' : ''}');
    if (stackTrace != null) {
      debugPrint(stackTrace.toString());
    }
  }
}
