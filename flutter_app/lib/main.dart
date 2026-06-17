import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'app_state.dart';
import 'config/app_config.dart';
import 'features/auth/login_screen.dart';
import 'features/room/room_screen.dart';
import 'services/auth_service.dart';
import 'services/local_db_service.dart';
import 'services/signaling_service.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const SecureP2PChatApp());
}

class SecureP2PChatApp extends StatefulWidget {
  const SecureP2PChatApp({super.key});

  @override
  State<SecureP2PChatApp> createState() => _SecureP2PChatAppState();
}

class _SecureP2PChatAppState extends State<SecureP2PChatApp> {
  late final AppState _appState;
  bool _ready = false;

  @override
  void initState() {
    super.initState();
    _init();
  }

  Future<void> _init() async {
    _appState = AppState(
      serverUrl: AppConfig.serverUrl,
      authService: AuthService(AppConfig.serverUrl),
      signaling: SignalingService(AppConfig.serverUrl),
      localDb: LocalDbService(),
    );
    await _appState.initialize();
    setState(() => _ready = true);
  }

  @override
  Widget build(BuildContext context) {
    if (!_ready) {
      return const MaterialApp(
        home: Scaffold(body: Center(child: CircularProgressIndicator())),
      );
    }

    return ChangeNotifierProvider.value(
      value: _appState,
      child: MaterialApp(
        title: 'Secure P2P Chat',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF1565C0)),
          useMaterial3: true,
        ),
        home: _appState.isLoggedIn ? const RoomScreen() : const LoginScreen(),
      ),
    );
  }
}
