class ChatUser {
  const ChatUser({
    required this.username,
    required this.publicKey,
    this.online = false,
  });

  final String username;
  final String publicKey;
  final bool online;

  factory ChatUser.fromJson(Map<String, dynamic> json) {
    return ChatUser(
      username: json['username'] as String,
      publicKey: json['publicKey'] as String? ?? '',
      online: json['online'] as bool? ?? false,
    );
  }
}
