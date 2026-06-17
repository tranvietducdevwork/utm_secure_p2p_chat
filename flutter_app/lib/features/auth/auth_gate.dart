import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../app_state.dart';
import 'login_screen.dart';
import '../room/room_screen.dart';

/// Chuyển Login ↔ Room theo [AppState.isLoggedIn].
/// MaterialApp.home luôn là widget này — không đổi home sau khi app chạy.
class AuthGate extends StatelessWidget {
  const AuthGate({super.key});

  @override
  Widget build(BuildContext context) {
    final isLoggedIn = context.watch<AppState>().isLoggedIn;
    return isLoggedIn ? const RoomScreen() : const LoginScreen();
  }
}
