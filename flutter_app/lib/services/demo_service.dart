import 'dart:convert';

import 'package:http/http.dart' as http;

import '../config/app_config.dart';
import '../core/log/app_logger.dart';

class DemoSettings {
  const DemoSettings({
    required this.storeMessagesOnServer,
    required this.storePlaintextOnServer,
  });

  final bool storeMessagesOnServer;
  final bool storePlaintextOnServer;

  factory DemoSettings.fromJson(Map<String, dynamic> json) {
    return DemoSettings(
      storeMessagesOnServer: json['storeMessagesOnServer'] as bool? ?? false,
      storePlaintextOnServer: json['storePlaintextOnServer'] as bool? ?? false,
    );
  }

  DemoSettings copyWith({bool? storeMessagesOnServer, bool? storePlaintextOnServer}) {
    return DemoSettings(
      storeMessagesOnServer: storeMessagesOnServer ?? this.storeMessagesOnServer,
      storePlaintextOnServer: storePlaintextOnServer ?? this.storePlaintextOnServer,
    );
  }
}

class DemoService {
  DemoService(this.serverUrl);

  final String serverUrl;

  Future<DemoSettings> fetchSettings() async {
    final response = await http
        .get(Uri.parse('$serverUrl/api/demo/settings'))
        .timeout(AppConfig.signalingTimeout);
    if (response.statusCode != 200) {
      throw Exception('Không tải được cài đặt demo (HTTP ${response.statusCode})');
    }
    return DemoSettings.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }

  Future<DemoSettings> updateSettings({
    bool? storeMessagesOnServer,
    bool? storePlaintextOnServer,
    bool clearMessages = false,
  }) async {
    AppLogger.i('Demo', 'update settings store=$storeMessagesOnServer plaintext=$storePlaintextOnServer');
    final response = await http
        .post(
          Uri.parse('$serverUrl/api/demo/settings'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({
            if (storeMessagesOnServer != null) 'storeMessagesOnServer': storeMessagesOnServer,
            if (storePlaintextOnServer != null) 'storePlaintextOnServer': storePlaintextOnServer,
            if (clearMessages) 'clearMessages': true,
          }),
        )
        .timeout(AppConfig.signalingTimeout);
    if (response.statusCode != 200) {
      throw Exception('Không cập nhật được cài đặt demo');
    }
    return DemoSettings.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }

  String get healthPageUrl => '$serverUrl/health';
}
