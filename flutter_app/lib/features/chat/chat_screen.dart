import 'dart:async';

import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

import '../../app_state.dart';
import '../../core/chat/chat_session.dart';
import '../../models/message.dart';
import '../../models/user.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key, required this.peer});

  final ChatUser peer;

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final _textController = TextEditingController();
  final _scrollController = ScrollController();
  ChatSession? _session;
  ChatTransportMode _mode = ChatTransportMode.connecting;
  StreamSubscription? _modeSub;
  bool _connecting = true;

  @override
  void initState() {
    super.initState();
    _initChat();
  }

  Future<void> _initChat() async {
    final app = context.read<AppState>();
    await app.loadMessages(widget.peer.username);
    try {
      _session = await app.connectToPeer(widget.peer);
      _modeSub = _session!.modeStream.listen((mode) {
        if (mounted) setState(() => _mode = mode);
      });
      setState(() {
        _mode = _session!.mode;
        _connecting = false;
      });
    } catch (e) {
      setState(() {
        _connecting = false;
        _mode = ChatTransportMode.failed;
      });
    }
  }

  Future<void> _send() async {
    final text = _textController.text.trim();
    if (text.isEmpty) return;
    final app = context.read<AppState>();
    try {
      await app.sendMessage(widget.peer.username, text);
      _textController.clear();
      _scrollToBottom();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Gửi thất bại: $e')),
      );
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 200),
          curve: Curves.easeOut,
        );
      }
    });
  }

  Color _statusColor() {
    switch (_mode) {
      case ChatTransportMode.p2p:
      case ChatTransportMode.relay:
        return Colors.green;
      case ChatTransportMode.connecting:
        return Colors.orange;
      case ChatTransportMode.failed:
        return Colors.red;
    }
  }

  String _statusText() {
    switch (_mode) {
      case ChatTransportMode.p2p:
        return 'P2P trực tiếp • E2E';
      case ChatTransportMode.relay:
        return 'Relay E2E (emulator/NAT) • vẫn mã hóa';
      case ChatTransportMode.connecting:
        return 'Đang thiết lập kết nối...';
      case ChatTransportMode.failed:
        return 'Kết nối thất bại';
    }
  }

  bool get _canSend => _session?.canSend == true;

  @override
  void dispose() {
    _modeSub?.cancel();
    _textController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final app = context.watch<AppState>();
    final messages = app.messagesFor(widget.peer.username);

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(widget.peer.username),
            Row(
              children: [
                Container(
                  width: 8,
                  height: 8,
                  decoration: BoxDecoration(
                    color: _statusColor(),
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 6),
                Flexible(
                  child: Text(
                    _statusText(),
                    style: Theme.of(context).textTheme.bodySmall,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
      body: Column(
        children: [
          if (_connecting) const LinearProgressIndicator(),
          Container(
            width: double.infinity,
            color: Colors.blue.shade50,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: Text(
              _mode == ChatTransportMode.relay
                  ? '2 emulator thường không P2P trực tiếp. App chuyển relay E2E qua signaling — server chỉ chuyển tiếp, không lưu tin.'
                  : 'Tin nhắn mã hóa E2E. Server không lưu nội dung.',
              style: const TextStyle(fontSize: 12),
            ),
          ),
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.all(12),
              itemCount: messages.length,
              itemBuilder: (context, index) {
                return _MessageBubble(message: messages[index]);
              },
            ),
          ),
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(8),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _textController,
                      decoration: const InputDecoration(
                        hintText: 'Nhập tin nhắn...',
                        border: OutlineInputBorder(),
                        contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                      ),
                      onSubmitted: (_) => _send(),
                    ),
                  ),
                  const SizedBox(width: 8),
                  IconButton.filled(
                    onPressed: _canSend ? _send : null,
                    icon: const Icon(Icons.send),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _MessageBubble extends StatelessWidget {
  const _MessageBubble({required this.message});

  final ChatMessage message;

  @override
  Widget build(BuildContext context) {
    final time = DateFormat('HH:mm').format(message.timestamp);
    return Align(
      alignment: message.isMine ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 4),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.75),
        decoration: BoxDecoration(
          color: message.isMine ? Colors.blue.shade600 : Colors.grey.shade200,
          borderRadius: BorderRadius.circular(16),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              message.content,
              style: TextStyle(color: message.isMine ? Colors.white : Colors.black87),
            ),
            const SizedBox(height: 4),
            Text(
              '$time ${message.encrypted ? '🔒' : ''}',
              style: TextStyle(
                fontSize: 10,
                color: message.isMine ? Colors.white70 : Colors.grey,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
