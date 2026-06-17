class ChatMessage {
  const ChatMessage({
    required this.id,
    required this.peerUsername,
    required this.content,
    required this.isMine,
    required this.timestamp,
    required this.encrypted,
  });

  final int? id;
  final String peerUsername;
  final String content;
  final bool isMine;
  final DateTime timestamp;
  final bool encrypted;

  Map<String, dynamic> toMap() => {
        'id': id,
        'peer_username': peerUsername,
        'content': content,
        'is_mine': isMine ? 1 : 0,
        'timestamp': timestamp.millisecondsSinceEpoch,
        'encrypted': encrypted ? 1 : 0,
      };

  factory ChatMessage.fromMap(Map<String, dynamic> map) {
    return ChatMessage(
      id: map['id'] as int?,
      peerUsername: map['peer_username'] as String,
      content: map['content'] as String,
      isMine: (map['is_mine'] as int) == 1,
      timestamp: DateTime.fromMillisecondsSinceEpoch(map['timestamp'] as int),
      encrypted: (map['encrypted'] as int) == 1,
    );
  }
}
