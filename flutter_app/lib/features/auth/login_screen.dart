import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../app_state.dart';
import '../../core/errors/app_errors.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isRegister = false;
  bool _loading = false;
  String? _error;
  String? _status;

  Future<void> _submit() async {
    setState(() {
      _loading = true;
      _error = null;
      _status = _isRegister ? 'Đang đăng ký...' : 'Đang đăng nhập...';
    });
    try {
      final app = context.read<AppState>();
      final username = _usernameController.text.trim();
      final password = _passwordController.text;

      if (username.length < 3) {
        throw Exception('Tên đăng nhập tối thiểu 3 ký tự');
      }
      if (password.length < 6) {
        throw Exception('Mật khẩu tối thiểu 6 ký tự');
      }

      setState(() => _status = 'Đang kết nối server (có thể mất ~1 phút)...');

      if (_isRegister) {
        await app.register(username, password);
      } else {
        await app.login(username, password);
      }
      if (!mounted) return;
      if (!app.isLoggedIn) {
        throw Exception('Đăng nhập thất bại');
      }
      // AuthGate tự chuyển sang RoomScreen khi isLoggedIn = true
    } catch (e) {
      setState(() => _error = AppErrors.friendly(e, context: _isRegister ? 'Đăng ký' : 'Đăng nhập'));
    } finally {
      if (mounted) {
        setState(() {
          _loading = false;
          _status = null;
        });
      }
    }
  }

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 40),
              Icon(Icons.lock_outline, size: 72, color: Theme.of(context).colorScheme.primary),
              const SizedBox(height: 16),
              Text(
                'Secure P2P Chat',
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              Text(
                'Đăng nhập → nhập mã phòng → chat qua 4G/WiFi',
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: Colors.grey[600]),
              ),
              const SizedBox(height: 32),
              TextField(
                controller: _usernameController,
                decoration: const InputDecoration(
                  labelText: 'Tên đăng nhập',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.person),
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: _passwordController,
                obscureText: true,
                decoration: const InputDecoration(
                  labelText: 'Mật khẩu',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.key),
                  helperText: 'Tối thiểu 6 ký tự',
                ),
              ),
              if (_status != null) ...[
                const SizedBox(height: 16),
                Row(
                  children: [
                    const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    ),
                    const SizedBox(width: 10),
                    Expanded(child: Text(_status!, style: TextStyle(color: Colors.grey[700]))),
                  ],
                ),
              ],
              if (_error != null) ...[
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.red.shade50,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(_error!, style: TextStyle(color: Colors.red.shade900)),
                ),
              ],
              const SizedBox(height: 24),
              FilledButton(
                onPressed: _loading ? null : _submit,
                child: Padding(
                  padding: const EdgeInsets.symmetric(vertical: 12),
                  child: Text(_isRegister ? 'Đăng ký' : 'Đăng nhập'),
                ),
              ),
              TextButton(
                onPressed: _loading ? null : () => setState(() => _isRegister = !_isRegister),
                child: Text(_isRegister ? 'Đã có tài khoản? Đăng nhập' : 'Chưa có tài khoản? Đăng ký'),
              ),
              if (!_isRegister) ...[
                const SizedBox(height: 8),
                Text(
                  'Nếu đăng nhập báo "Invalid credentials": server có thể đã khởi động lại — hãy đăng ký lại tài khoản.',
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(color: Colors.grey[600]),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
