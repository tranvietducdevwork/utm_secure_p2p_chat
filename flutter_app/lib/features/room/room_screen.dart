import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';

import '../../app_state.dart';
import '../../config/app_config.dart';
import '../../models/user.dart';
import '../chat/chat_screen.dart';

class RoomScreen extends StatefulWidget {
  const RoomScreen({super.key});

  @override
  State<RoomScreen> createState() => _RoomScreenState();
}

class _RoomScreenState extends State<RoomScreen> {
  final _roomController = TextEditingController();
  bool _loading = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final app = context.read<AppState>();
      if (app.currentRoomCode != null) {
        app.refreshRoomPeers();
      }
    });
  }

  Future<void> _joinRoom() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      await context.read<AppState>().joinRoom(_roomController.text);
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _leaveRoom() async {
    await context.read<AppState>().leaveRoom();
    _roomController.clear();
  }

  @override
  void dispose() {
    _roomController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final app = context.watch<AppState>();
    final inRoom = app.currentRoomCode != null;
    final peers = app.roomPeers;

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Secure P2P Chat'),
            Text(
              app.currentUser?.username ?? '',
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ),
        actions: [
          if (inRoom)
            IconButton(
              icon: const Icon(Icons.refresh),
              onPressed: () => app.refreshRoomPeers(),
            ),
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () async {
              await app.logout();
              if (!context.mounted) return;
              Navigator.of(context).popUntil((route) => route.isFirst);
            },
          ),
        ],
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: inRoom ? _buildLobby(context, app, peers) : _buildJoinForm(context),
        ),
      ),
    );
  }

  Widget _buildJoinForm(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Icon(Icons.meeting_room_outlined, size: 72, color: Theme.of(context).colorScheme.primary),
        const SizedBox(height: 16),
        Text(
          'Vào phòng chat',
          textAlign: TextAlign.center,
          style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        Text(
          'Hai người nhập cùng mã phòng để kết nối qua 4G hoặc WiFi',
          textAlign: TextAlign.center,
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: Colors.grey[600]),
        ),
        const SizedBox(height: 8),
        Text(
          'Server: ${AppConfig.serverUrl}',
          textAlign: TextAlign.center,
          style: Theme.of(context).textTheme.bodySmall?.copyWith(color: Colors.grey[500]),
        ),
        const SizedBox(height: 32),
        TextField(
          controller: _roomController,
          textCapitalization: TextCapitalization.characters,
          inputFormatters: [
            FilteringTextInputFormatter.allow(RegExp(r'[A-Za-z0-9]')),
            LengthLimitingTextInputFormatter(12),
          ],
          decoration: const InputDecoration(
            labelText: 'Mã phòng',
            hintText: 'VD: PHONG01',
            border: OutlineInputBorder(),
            prefixIcon: Icon(Icons.tag),
          ),
        ),
        if (_error != null) ...[
          const SizedBox(height: 12),
          Text(_error!, style: const TextStyle(color: Colors.red)),
        ],
        const SizedBox(height: 24),
        FilledButton(
          onPressed: _loading ? null : _joinRoom,
          child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 14),
            child: _loading
                ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2))
                : const Text('Vào phòng'),
          ),
        ),
      ],
    );
  }

  Widget _buildLobby(BuildContext context, AppState app, List<ChatUser> peers) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Card(
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              children: [
                Text('Mã phòng', style: Theme.of(context).textTheme.labelLarge),
                const SizedBox(height: 8),
                SelectableText(
                  app.currentRoomCode!,
                  style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                        letterSpacing: 4,
                      ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Gửi mã này cho người kia để cùng vào phòng',
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(color: Colors.grey[600]),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 24),
        Text(
          'Người trong phòng (${peers.length})',
          style: Theme.of(context).textTheme.titleMedium,
        ),
        const SizedBox(height: 12),
        Expanded(
          child: peers.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.hourglass_empty, size: 56, color: Colors.grey[400]),
                      const SizedBox(height: 12),
                      const Text('Đang chờ người khác vào phòng...'),
                      const SizedBox(height: 8),
                      Text(
                        'Người kia cần đăng nhập và nhập cùng mã phòng',
                        textAlign: TextAlign.center,
                        style: TextStyle(color: Colors.grey[600]),
                      ),
                    ],
                  ),
                )
              : ListView.separated(
                  itemCount: peers.length,
                  separatorBuilder: (_, __) => const Divider(height: 1),
                  itemBuilder: (context, index) {
                    final peer = peers[index];
                    return ListTile(
                      leading: CircleAvatar(
                        backgroundColor: Colors.green.shade100,
                        child: Text(peer.username[0].toUpperCase()),
                      ),
                      title: Text(peer.username),
                      subtitle: const Text('Sẵn sàng chat • E2E'),
                      trailing: const Icon(Icons.chat_bubble_outline),
                      onTap: () {
                        Navigator.of(context).push(
                          MaterialPageRoute(builder: (_) => ChatScreen(peer: peer)),
                        );
                      },
                    );
                  },
                ),
        ),
        OutlinedButton(
          onPressed: _leaveRoom,
          child: const Padding(
            padding: EdgeInsets.symmetric(vertical: 12),
            child: Text('Rời phòng'),
          ),
        ),
      ],
    );
  }
}
