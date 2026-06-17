/// Cấu hình server signaling.
///
/// Sau khi deploy server lên cloud, đổi [cloudSignalingUrl] thành URL thật
/// (ví dụ https://secure-p2p-chat.onrender.com).
///
/// Hoặc build với:
/// flutter run --dart-define=SIGNALING_URL=https://your-server.com
class AppConfig {
  static const cloudSignalingUrl = String.fromEnvironment(
    'SIGNALING_URL',
    defaultValue: 'https://utm-secure-p2p-chat.onrender.com',
  );

  /// URL signaling — dùng server cloud, hoạt động trên 4G/WiFi.
  static String get serverUrl => cloudSignalingUrl;

  /// Timeout chờ server cloud (Render free tier có thể ngủ ~30–90s).
  static const signalingTimeout = Duration(seconds: 90);

  /// Timeout thử WebRTC P2P trước khi chuyển relay.
  static const p2pConnectTimeout = Duration(seconds: 8);

  static const stunServers = [
    {'urls': 'stun:stun.l.google.com:19302'},
    {'urls': 'stun:stun1.l.google.com:19302'},
  ];
}
