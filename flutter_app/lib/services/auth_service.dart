import 'dart:convert';

import 'package:cryptography/cryptography.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

import '../core/crypto/e2e_crypto.dart';
import '../models/user.dart';

class AuthService {
  AuthService(this.serverUrl);

  final String serverUrl;
  static const _tokenKey = 'auth_token';
  static const _usernameKey = 'username';
  static const _privateKeyKey = 'private_key_base64';
  static const _publicKeyKey = 'public_key_base64';

  Future<ChatUser> register({
    required String username,
    required String password,
  }) async {
    final keyPair = await E2ECrypto.generateKeyPair();
    final publicKey = await keyPair.extractPublicKey();
    final publicKeyBase64 = await E2ECrypto.publicKeyToBase64(publicKey);
    final privateKeyBase64 = await E2ECrypto.privateKeyToBase64(keyPair);

    final response = await http.post(
      Uri.parse('$serverUrl/api/register'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'username': username,
        'password': password,
        'publicKey': publicKeyBase64,
      }),
    );

    if (response.statusCode != 201) {
      final body = jsonDecode(response.body) as Map<String, dynamic>;
      throw Exception(body['error'] ?? 'Registration failed');
    }

    final data = jsonDecode(response.body) as Map<String, dynamic>;
    await _persistSession(
      token: data['token'] as String,
      username: username,
      privateKeyBase64: privateKeyBase64,
      publicKeyBase64: publicKeyBase64,
    );
    await _syncPublicKeyToServer(data['token'] as String, publicKeyBase64);
    return ChatUser.fromJson(data['user'] as Map<String, dynamic>);
  }

  Future<ChatUser> login({
    required String username,
    required String password,
  }) async {
    final response = await http.post(
      Uri.parse('$serverUrl/api/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'username': username, 'password': password}),
    );

    if (response.statusCode != 200) {
      final body = jsonDecode(response.body) as Map<String, dynamic>;
      throw Exception(body['error'] ?? 'Login failed');
    }

    final data = jsonDecode(response.body) as Map<String, dynamic>;
    final user = ChatUser.fromJson(data['user'] as Map<String, dynamic>);
    final token = data['token'] as String;

    final prefs = await SharedPreferences.getInstance();
    var privateKeyBase64 = prefs.getString(_privateKeyKey);
    var publicKeyBase64 = prefs.getString(_publicKeyKey);

    if (privateKeyBase64 == null || publicKeyBase64 == null) {
      final keyPair = await E2ECrypto.generateKeyPair();
      final publicKey = await keyPair.extractPublicKey();
      publicKeyBase64 = await E2ECrypto.publicKeyToBase64(publicKey);
      privateKeyBase64 = await E2ECrypto.privateKeyToBase64(keyPair);
    }

    await _persistSession(
      token: token,
      username: username,
      privateKeyBase64: privateKeyBase64,
      publicKeyBase64: publicKeyBase64,
    );
    await _syncPublicKeyToServer(token, publicKeyBase64);
    return user;
  }

  Future<void> _syncPublicKeyToServer(String token, String publicKeyBase64) async {
    await http.post(
      Uri.parse('$serverUrl/api/sync-public-key'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode({'publicKey': publicKeyBase64}),
    );
  }

  Future<void> _persistSession({
    required String token,
    required String username,
    required String privateKeyBase64,
    required String publicKeyBase64,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, token);
    await prefs.setString(_usernameKey, username);
    await prefs.setString(_privateKeyKey, privateKeyBase64);
    await prefs.setString(_publicKeyKey, publicKeyBase64);
  }

  Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_tokenKey);
  }

  Future<String?> getUsername() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_usernameKey);
  }

  Future<SimpleKeyPair?> getLocalKeyPair() async {
    final prefs = await SharedPreferences.getInstance();
    final privateKey = prefs.getString(_privateKeyKey);
    if (privateKey == null) return null;
    return E2ECrypto.keyPairFromPrivateBase64(privateKey);
  }

  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
    await prefs.remove(_usernameKey);
  }

  Future<String> fetchPublicKey(String username) async {
    final response = await http.get(
      Uri.parse('$serverUrl/api/users/$username/public-key'),
    );
    if (response.statusCode != 200) {
      throw Exception('Cannot fetch public key for $username');
    }
    final data = jsonDecode(response.body) as Map<String, dynamic>;
    return data['publicKey'] as String;
  }

}
