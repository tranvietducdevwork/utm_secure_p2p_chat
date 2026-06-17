import 'dart:async';

import 'package:cryptography/cryptography.dart';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'core/chat/chat_session.dart';
import 'core/errors/app_errors.dart';
import 'core/log/app_logger.dart';
import 'models/message.dart';
import 'models/user.dart';
import 'services/auth_service.dart';
import 'services/local_db_service.dart';
import 'services/signaling_service.dart';

class AppState extends ChangeNotifier {
  static final navigatorKey = GlobalKey<NavigatorState>();

  AppState({
    required String serverUrl,
    AuthService? authService,
    SignalingService? signaling,
    LocalDbService? localDb,
  })  : serverUrl = serverUrl,
        authService = authService ?? AuthService(serverUrl),
        signaling = signaling ?? SignalingService(serverUrl),
        localDb = localDb ?? LocalDbService();

  static const _roomKey = 'last_room_code';

  String serverUrl;
  AuthService authService;
  final SignalingService signaling;
  final LocalDbService localDb;

  ChatUser? currentUser;
  SimpleKeyPair? localKeyPair;
  String? currentRoomCode;
  String? lastError;
  String connectionStatus = '';

  final Map<String, ChatSession> _sessions = {};
  final Map<String, List<ChatMessage>> _chatCache = {};
  bool _signalingWired = false;

  bool get isLoggedIn => currentUser != null;
  bool get isSignalingConnected => signaling.isConnected;
  List<ChatUser> get roomPeers => signaling.roomUsers;

  /// Khởi động nhanh — không chặn UI chờ server cloud.
  Future<void> initialize() async {
    AppLogger.i('AppState', 'initialize() start');
    try {
      final token = await authService.getToken();
      final username = await authService.getUsername();
      localKeyPair = await authService.getLocalKeyPair();
      _wireSignaling();

      if (token != null && username != null) {
        AppLogger.i('AppState', 'Khôi phục phiên: $username');
        currentUser = ChatUser(username: username, publicKey: '', online: false);
        final prefs = await SharedPreferences.getInstance();
        currentRoomCode = prefs.getString(_roomKey);
        notifyListeners();
        unawaited(_connectSignalingInBackground(token));
      } else {
        AppLogger.i('AppState', 'Chưa có phiên đăng nhập');
      }
    } catch (e, st) {
      AppLogger.e('AppState', 'initialize() lỗi', e, st);
      lastError = AppErrors.friendly(e, context: 'Khởi động app');
      rethrow;
    }
  }

  Future<void> _connectSignalingInBackground(String token) async {
    connectionStatus = 'Đang kết nối server...';
    lastError = null;
    notifyListeners();

    try {
      AppLogger.i('AppState', 'Kết nối signaling...');
      await signaling.connect(token);
      currentUser = currentUser?.copyWith(online: true);
      connectionStatus = '';
      AppLogger.i('AppState', 'Signaling đã kết nối');

      final savedRoom = currentRoomCode;
      if (savedRoom != null && savedRoom.isNotEmpty) {
        connectionStatus = 'Đang vào lại phòng $savedRoom...';
        notifyListeners();
        try {
          await joinRoom(savedRoom);
          AppLogger.i('AppState', 'Vào lại phòng $savedRoom thành công');
        } catch (e) {
          AppLogger.w('AppState', 'Không vào lại được phòng: $e');
          currentRoomCode = null;
          final prefs = await SharedPreferences.getInstance();
          await prefs.remove(_roomKey);
          lastError = AppErrors.friendly(e, context: 'Vào phòng');
        }
      }
    } catch (e, st) {
      AppLogger.e('AppState', 'Kết nối signaling thất bại', e, st);
      lastError = AppErrors.friendly(e, context: 'Kết nối server');
      connectionStatus = 'Chưa kết nối server';
    } finally {
      if (connectionStatus.startsWith('Đang')) {
        connectionStatus = signaling.isConnected ? '' : 'Chưa kết nối server';
      }
      notifyListeners();
    }
  }

  Future<void> retrySignalingConnection() async {
    final token = await authService.getToken();
    if (token == null) {
      lastError = 'Chưa đăng nhập';
      notifyListeners();
      return;
    }
    await _connectSignalingInBackground(token);
  }

  void clearLastError() {
    lastError = null;
    notifyListeners();
  }

  void _wireSignaling() {
    if (_signalingWired) return;
    _signalingWired = true;

    signaling.onRoomUsersChanged = (_) => notifyListeners();
    signaling.onRoomJoined = (code) {
      currentRoomCode = code;
      notifyListeners();
    };
    signaling.onRoomError = (msg) {
      AppLogger.w('AppState', 'Room error: $msg');
      lastError = msg;
      notifyListeners();
    };
    signaling.onConnectionError = (msg) {
      AppLogger.e('AppState', 'Socket error: $msg');
      lastError = msg;
      connectionStatus = 'Mất kết nối server';
      notifyListeners();
    };

    signaling.onWebRtcOffer = (data) async {
      final from = data['from'] as String? ?? '';
      final offer = data['offer'];
      if (from.isEmpty || offer is! Map) return;
      final peer = await _resolvePeer(from);
      final session = await _getOrCreateSession(peer, isInitiator: false);
      await session.handleOffer(Map<String, dynamic>.from(offer));
    };

    signaling.onWebRtcAnswer = (data) async {
      final from = data['from'] as String? ?? '';
      final answer = data['answer'];
      if (from.isEmpty || answer is! Map) return;
      await _sessions[from]?.handleAnswer(Map<String, dynamic>.from(answer));
    };

    signaling.onIceCandidate = (data) async {
      final from = data['from'] as String? ?? '';
      final candidate = data['candidate'];
      if (from.isEmpty || candidate is! Map) return;
      await _sessions[from]?.handleIceCandidate(Map<String, dynamic>.from(candidate));
    };

    signaling.onEncryptedMessage = (data) async {
      final from = data['from'] as String? ?? '';
      final payload = data['payload']?.toString() ?? '';
      if (from.isEmpty || payload.isEmpty) return;

      ChatSession? session = _sessions[from];
      if (session == null) {
        final peer = await _resolvePeer(from);
        session = await _getOrCreateSession(peer, isInitiator: false);
      }
      await session.handleRelayPayload(payload);
    };
  }

  Future<ChatUser> _resolvePeer(String username) async {
    final inRoom = roomPeers.where((u) => u.username == username);
    if (inRoom.isNotEmpty && inRoom.first.publicKey.isNotEmpty) {
      return inRoom.first;
    }
    final pk = await authService.fetchPublicKey(username);
    return ChatUser(username: username, publicKey: pk, online: true);
  }

  Future<void> register(String username, String password) async {
    _wireSignaling();
    AppLogger.i('AppState', 'Đăng ký: $username');
    lastError = null;
    currentUser = await authService.register(username: username, password: password);
    localKeyPair = await authService.getLocalKeyPair();
    notifyListeners();
    final token = await authService.getToken();
    if (token != null) unawaited(_connectSignalingInBackground(token));
  }

  Future<void> login(String username, String password) async {
    _wireSignaling();
    AppLogger.i('AppState', 'Đăng nhập: $username');
    lastError = null;
    currentUser = await authService.login(username: username, password: password);
    localKeyPair = await authService.getLocalKeyPair();
    notifyListeners();
    final token = await authService.getToken();
    if (token != null) unawaited(_connectSignalingInBackground(token));
  }

  Future<void> joinRoom(String roomCode) async {
    final code = roomCode.trim().toUpperCase();
    if (code.length < 4) {
      throw Exception('Mã phòng tối thiểu 4 ký tự');
    }
    AppLogger.i('AppState', 'Vào phòng: $code');
    lastError = null;
    await signaling.joinRoom(code);
    currentRoomCode = signaling.roomCode ?? code;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_roomKey, currentRoomCode!);
    notifyListeners();
  }

  Future<void> leaveRoom() async {
    signaling.leaveRoom();
    currentRoomCode = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_roomKey);
    notifyListeners();
  }

  void refreshRoomPeers() {
    signaling.refreshRoomUsers();
    notifyListeners();
  }

  Future<void> logout() async {
    AppLogger.i('AppState', 'Đăng xuất');
    await leaveRoom();
    for (final session in _sessions.values) {
      await session.dispose();
    }
    _sessions.clear();
    await signaling.disconnect();
    await authService.logout();
    currentUser = null;
    lastError = null;
    connectionStatus = '';
    notifyListeners();
    navigatorKey.currentState?.popUntil((route) => route.isFirst);
  }

  List<ChatMessage> messagesFor(String peerUsername) {
    return List.unmodifiable(_chatCache[peerUsername] ?? []);
  }

  ChatSession? sessionFor(String peerUsername) => _sessions[peerUsername];

  Future<List<ChatMessage>> loadMessages(String peerUsername) async {
    final messages = await localDb.getMessages(peerUsername);
    _chatCache[peerUsername] = messages;
    notifyListeners();
    return messages;
  }

  Future<ChatSession> connectToPeer(ChatUser peer) async {
    return _getOrCreateSession(peer, isInitiator: true);
  }

  Future<ChatSession> _getOrCreateSession(
    ChatUser peer, {
    required bool isInitiator,
  }) async {
    if (_sessions.containsKey(peer.username)) {
      return _sessions[peer.username]!;
    }
    if (localKeyPair == null) {
      throw Exception('Missing local key pair');
    }

    var publicKey = peer.publicKey;
    if (publicKey.isEmpty) {
      publicKey = await authService.fetchPublicKey(peer.username);
    }

    final session = ChatSession(
      signaling: signaling,
      localUsername: currentUser!.username,
      localKeyPair: localKeyPair!,
      remoteUsername: peer.username,
      remotePublicKeyBase64: publicKey,
      isInitiator: isInitiator,
      onIncomingMessage: (text) {
        unawaited(_onIncomingMessage(peer.username, text));
      },
    );
    await session.start();
    _sessions[peer.username] = session;
    return session;
  }

  Future<void> _onIncomingMessage(String peerUsername, String text) async {
    final message = ChatMessage(
      id: null,
      peerUsername: peerUsername,
      content: text,
      isMine: false,
      timestamp: DateTime.now(),
      encrypted: true,
    );
    await _appendMessage(message);
  }

  Future<void> sendMessage(String peerUsername, String text) async {
    var session = _sessions[peerUsername];
    if (session == null) {
      final peer = await _resolvePeer(peerUsername);
      session = await _getOrCreateSession(peer, isInitiator: true);
    }
    final ok = await session.sendMessage(text);
    if (!ok) throw Exception('Kênh chat chưa sẵn sàng');
    final message = ChatMessage(
      id: null,
      peerUsername: peerUsername,
      content: text,
      isMine: true,
      timestamp: DateTime.now(),
      encrypted: true,
    );
    await _appendMessage(message);
  }

  Future<void> _appendMessage(ChatMessage message) async {
    await localDb.saveMessage(message);
    _chatCache.putIfAbsent(message.peerUsername, () => []);
    _chatCache[message.peerUsername]!.add(message);
    notifyListeners();
  }
}
