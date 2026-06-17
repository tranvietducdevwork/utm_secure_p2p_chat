import 'dart:async';
import 'dart:io';

import 'package:http/http.dart' as http;

class AppErrors {
  static String friendly(Object error, {String? context}) {
    final prefix = context != null ? '$context: ' : '';

    if (error is TimeoutException) {
      return '${prefix}Server đang khởi động (quá thời gian chờ). '
          'Đợi ~1 phút hoặc mở URL server /health trên trình duyệt rồi thử lại.';
    }

    if (error is SocketException) {
      return '${prefix}Không có mạng hoặc không kết nối được server.';
    }

    if (error is http.ClientException) {
      return '${prefix}Lỗi kết nối HTTP: ${error.message}';
    }

    if (error is FormatException) {
      return '${prefix}Phản hồi server không hợp lệ.';
    }

    final text = error.toString();
    if (text.startsWith('Exception: ')) {
      return text.substring('Exception: '.length);
    }
    return '$prefix$text';
  }

  static String authHttpError(int statusCode, String? serverError) {
    switch (statusCode) {
      case 401:
        return serverError ??
            'Sai tên đăng nhập/mật khẩu. '
                'Nếu server Render vừa khởi động lại, tài khoản cũ có thể mất — hãy đăng ký lại.';
      case 409:
        return serverError ?? 'Tên đăng nhập đã tồn tại.';
      case 400:
        return serverError ?? 'Dữ liệu không hợp lệ.';
      default:
        return serverError ?? 'Lỗi server (HTTP $statusCode).';
    }
  }
}
