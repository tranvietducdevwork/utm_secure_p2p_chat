import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'app_state.dart';
import 'config/app_config.dart';
import 'core/errors/app_errors.dart';
import 'core/log/app_logger.dart';
import 'features/auth/auth_gate.dart';
import 'services/auth_service.dart';
import 'services/local_db_service.dart';
import 'services/signaling_service.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  AppLogger.i('Main', 'App start — server=${AppConfig.serverUrl}');
  runApp(const SecureP2PChatApp());
}

class SecureP2PChatApp extends StatefulWidget {
  const SecureP2PChatApp({super.key});

  @override
  State<SecureP2PChatApp> createState() => _SecureP2PChatAppState();
}

class _SecureP2PChatAppState extends State<SecureP2PChatApp> {
  AppState? _appState;
  bool _ready = false;
  String? _fatalError;

  @override
  void initState() {
    super.initState();
    _init();
  }

  Future<void> _init() async {
    try {
      final appState = AppState(
        serverUrl: AppConfig.serverUrl,
        authService: AuthService(AppConfig.serverUrl),
        signaling: SignalingService(AppConfig.serverUrl),
        localDb: LocalDbService(),
      );
      await appState.initialize();
      if (!mounted) return;
      setState(() {
        _appState = appState;
        _ready = true;
      });
    } catch (e, st) {
      AppLogger.e('Main', 'init failed', e, st);
      if (!mounted) return;
      setState(() {
        _fatalError = AppErrors.friendly(e, context: 'Khởi động');
        _ready = true;
      });
    }
  }

  Future<void> _retryInit() async {
    setState(() {
      _ready = false;
      _fatalError = null;
      _appState = null;
    });
    await _init();
  }

  @override
  Widget build(BuildContext context) {
    if (!_ready) {
      return MaterialApp(
        home: Scaffold(
          body: Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const CircularProgressIndicator(),
                const SizedBox(height: 16),
                Text('Đang khởi động app...', style: TextStyle(color: Colors.grey[600])),
              ],
            ),
          ),
        ),
      );
    }

    if (_fatalError != null || _appState == null) {
      return MaterialApp(
        home: Scaffold(
          body: SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.error_outline, size: 64, color: Colors.red),
                  const SizedBox(height: 16),
                  const Text('Không khởi động được app', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 12),
                  Text(_fatalError ?? 'Lỗi không xác định', textAlign: TextAlign.center),
                  const SizedBox(height: 24),
                  FilledButton(onPressed: _retryInit, child: const Text('Thử lại')),
                ],
              ),
            ),
          ),
        ),
      );
    }

    return ChangeNotifierProvider.value(
      value: _appState!,
      child: MaterialApp(
        navigatorKey: AppState.navigatorKey,
        title: 'Secure P2P Chat',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF1565C0)),
          useMaterial3: true,
        ),
        home: const AuthGate(),
      ),
    );
  }
}
