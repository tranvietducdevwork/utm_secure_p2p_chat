import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';

import '../../app_state.dart';

class DemoSettingsSheet extends StatefulWidget {
  const DemoSettingsSheet({super.key});

  @override
  State<DemoSettingsSheet> createState() => _DemoSettingsSheetState();
}

class _DemoSettingsSheetState extends State<DemoSettingsSheet> {
  bool _loading = false;
  String? _error;

  Future<void> _run(Future<void> Function() action) async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      await action();
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final app = context.watch<AppState>();
    final demo = app.demoSettings;

    return Padding(
      padding: EdgeInsets.only(
        left: 20,
        right: 20,
        top: 20,
        bottom: MediaQuery.of(context).viewInsets.bottom + 20,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text('Demo hội đồng', style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 8),
          Text(
            'So sánh bảo mật E2E vs server lưu tin nhắn. Mở /health trên trình duyệt để xem bảng.',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(color: Colors.grey[700]),
          ),
          const SizedBox(height: 16),
          SwitchListTile(
            contentPadding: EdgeInsets.zero,
            title: const Text('Server lưu tin nhắn (demo)'),
            subtitle: const Text('TẮT = chế độ E2E an toàn (mặc định)'),
            value: demo.storeMessagesOnServer,
            onChanged: _loading
                ? null
                : (v) => _run(() => app.setDemoStoreMessages(v)),
          ),
          SwitchListTile(
            contentPadding: EdgeInsets.zero,
            title: const Text('Lưu plaintext trên server (không an toàn)'),
            subtitle: const Text('Chỉ bật để demo hacker đọc được nội dung'),
            value: demo.storePlaintextOnServer,
            onChanged: !demo.storeMessagesOnServer || _loading
                ? null
                : (v) => _run(() => app.setDemoStorePlaintext(v)),
          ),
          const SizedBox(height: 8),
          SelectableText(
            app.demoHealthUrl,
            style: TextStyle(color: Theme.of(context).colorScheme.primary, fontSize: 13),
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: _loading
                      ? null
                      : () {
                          Clipboard.setData(ClipboardData(text: app.demoHealthUrl));
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Đã copy URL /health')),
                          );
                        },
                  icon: const Icon(Icons.copy, size: 18),
                  label: const Text('Copy URL'),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: _loading ? null : () => _run(() => app.clearDemoMessages()),
                  icon: const Icon(Icons.delete_outline, size: 18),
                  label: const Text('Xóa log server'),
                ),
              ),
            ],
          ),
          if (_error != null) ...[
            const SizedBox(height: 12),
            Text(_error!, style: const TextStyle(color: Colors.red)),
          ],
          if (_loading) ...[
            const SizedBox(height: 12),
            const Center(child: CircularProgressIndicator()),
          ],
        ],
      ),
    );
  }
}
