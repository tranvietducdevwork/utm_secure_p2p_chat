import 'dart:async';

import 'package:socket_io_client/socket_io_client.dart' as io;

import '../config/app_config.dart';
import '../core/log/app_logger.dart';
import '../models/user.dart';

typedef SignalingCallback = void Function(Map<String, dynamic> data);

Map<String, dynamic> _asStringMap(dynamic data) {
  if (data is Map) {
    return data.map((k, v) => MapEntry(k.toString(), v));
  }
  return {};
}

class SignalingService {
  SignalingService(this.serverUrl);

  final String serverUrl;
  io.Socket? _socket;
  String? _token;
  Completer<void>? _authCompleter;

  final _roomUsers = <ChatUser>[];
  String? _roomCode;

  List<ChatUser> get roomUsers => List.unmodifiable(_roomUsers);
  String? get roomCode => _roomCode;
  bool get isConnected => _socket?.connected ?? false;

  void Function(List<ChatUser>)? onRoomUsersChanged;
  void Function(String roomCode)? onRoomJoined;
  void Function(String)? onRoomError;
  void Function(String)? onConnectionError;
  SignalingCallback? onWebRtcOffer;
  SignalingCallback? onWebRtcAnswer;
  SignalingCallback? onIceCandidate;
  SignalingCallback? onEncryptedMessage;

  void _authenticate() {
    final token = _token;
    if (token == null) {
      AppLogger.e('Signaling', 'authenticate bỏ qua: token null');
      return;
    }
    if (_socket == null) return;
    AppLogger.d('Signaling', 'emit authenticate');
    _socket!.emit('authenticate', {'token': token});
  }

  void _setRoomUsers(List<ChatUser> users) {
    _roomUsers
      ..clear()
      ..addAll(users);
    onRoomUsersChanged?.call(roomUsers);
  }

  void _attachHandlers() {
    _socket!
      ..onConnect((_) {
        AppLogger.i('Signaling', 'socket connected');
        _authenticate();
      })
      ..onConnectError((err) {
        final msg = err?.toString() ?? 'connect_error';
        AppLogger.e('Signaling', 'onConnectError: $msg');
        onConnectionError?.call('Không kết nối được socket: $msg');
        if (_authCompleter != null && !_authCompleter!.isCompleted) {
          _authCompleter!.completeError(Exception(msg));
        }
      })
      ..onDisconnect((reason) {
        AppLogger.w('Signaling', 'disconnected: $reason');
      })
      ..on('authenticated', (data) {
        AppLogger.i('Signaling', 'authenticated: $data');
        _authCompleter?.complete();
        _authCompleter = null;
        if (_roomCode != null) {
          _socket!.emit('join-room', {'roomCode': _roomCode});
        }
      })
      ..on('auth-error', (data) {
        final map = _asStringMap(data);
        final msg = map['message'] as String? ?? 'Token không hợp lệ';
        AppLogger.e('Signaling', 'auth-error: $msg');
        onConnectionError?.call(msg);
        if (_authCompleter != null && !_authCompleter!.isCompleted) {
          _authCompleter!.completeError(Exception(msg));
        }
      })
      ..on('room-joined', (data) {
        AppLogger.i('Signaling', 'room-joined: $data');
        final map = _asStringMap(data);
        _roomCode = map['roomCode'] as String?;
        final users = (map['users'] as List<dynamic>? ?? [])
            .map((e) => ChatUser.fromJson(_asStringMap(e)))
            .toList();
        _setRoomUsers(users);
        if (_roomCode != null) {
          onRoomJoined?.call(_roomCode!);
        }
      })
      ..on('room-users', (data) {
        AppLogger.d('Signaling', 'room-users: $data');
        final map = _asStringMap(data);
        _roomCode = map['roomCode'] as String? ?? _roomCode;
        final users = (map['users'] as List<dynamic>? ?? [])
            .map((e) => ChatUser.fromJson(_asStringMap(e)))
            .toList();
        _setRoomUsers(users);
      })
      ..on('user-joined-room', (data) {
        AppLogger.i('Signaling', 'user-joined-room: $data');
        final map = _asStringMap(data);
        final user = ChatUser.fromJson(_asStringMap(map['user']));
        _roomCode = map['roomCode'] as String? ?? _roomCode;
        _roomUsers.removeWhere((u) => u.username == user.username);
        _roomUsers.add(user);
        onRoomUsersChanged?.call(roomUsers);
      })
      ..on('user-left-room', (data) {
        AppLogger.i('Signaling', 'user-left-room: $data');
        final map = _asStringMap(data);
        final username = map['username'] as String? ?? '';
        _roomUsers.removeWhere((u) => u.username == username);
        onRoomUsersChanged?.call(roomUsers);
      })
      ..on('room-left', (_) {
        AppLogger.i('Signaling', 'room-left');
        _roomCode = null;
        _roomUsers.clear();
        onRoomUsersChanged?.call(roomUsers);
      })
      ..on('room-error', (data) {
        final map = _asStringMap(data);
        final msg = map['message'] as String? ?? 'Không thể vào phòng';
        AppLogger.e('Signaling', 'room-error: $msg');
        onRoomError?.call(msg);
      })
      ..on('webrtc-offer', (data) => onWebRtcOffer?.call(_asStringMap(data)))
      ..on('webrtc-answer', (data) => onWebRtcAnswer?.call(_asStringMap(data)))
      ..on('ice-candidate', (data) => onIceCandidate?.call(_asStringMap(data)))
      ..on('e2e-message', (data) => onEncryptedMessage?.call(_asStringMap(data)));
  }

  Future<void> connect(String token) async {
    AppLogger.i('Signaling', 'connect to $serverUrl');
    await disconnect();
    _token = token;

    _authCompleter = Completer<void>();
    _socket = io.io(
      serverUrl,
      io.OptionBuilder()
          .setTransports(['websocket', 'polling'])
          .disableAutoConnect()
          .enableReconnection()
          .setReconnectionAttempts(20)
          .setReconnectionDelay(1000)
          .enableForceNew()
          .build(),
    );

    _attachHandlers();
    _socket!.connect();

    try {
      await _authCompleter!.future.timeout(AppConfig.signalingTimeout);
      AppLogger.i('Signaling', 'connect OK');
    } on TimeoutException {
      AppLogger.e('Signaling', 'auth timeout after ${AppConfig.signalingTimeout.inSeconds}s');
      throw Exception(
        'Server đang khởi động, quá thời gian chờ (${AppConfig.signalingTimeout.inSeconds}s). Thử lại sau.',
      );
    }
  }

  Future<void> _ensureConnected() async {
    if (_socket?.connected == true) return;
    final token = _token;
    if (token == null) {
      throw Exception('Chưa đăng nhập');
    }
    await connect(token);
    if (_socket?.connected != true) {
      throw Exception('Không kết nối được server signaling');
    }
  }

  Future<void> joinRoom(String roomCode) async {
    AppLogger.i('Signaling', 'joinRoom $roomCode');
    await _ensureConnected();

    final completer = Completer<void>();
    void onJoined(dynamic data) {
      if (!completer.isCompleted) completer.complete();
    }

    void onError(dynamic data) {
      if (!completer.isCompleted) {
        final map = _asStringMap(data);
        completer.completeError(map['message'] ?? 'Không thể vào phòng');
      }
    }

    _socket!.once('room-joined', onJoined);
    _socket!.once('room-error', onError);
    _socket!.emit('join-room', {'roomCode': roomCode.trim().toUpperCase()});

    try {
      await completer.future.timeout(AppConfig.signalingTimeout);
      AppLogger.i('Signaling', 'joinRoom OK');
    } on TimeoutException {
      AppLogger.e('Signaling', 'joinRoom timeout');
      throw Exception(
        'Vào phòng quá thời gian chờ. Server có thể đang khởi động — thử lại.',
      );
    } finally {
      _socket!.off('room-joined', onJoined);
      _socket!.off('room-error', onError);
    }
  }

  void refreshRoomUsers() {
    _socket?.emit('get-room-users');
  }

  void leaveRoom() {
    _socket?.emit('leave-room');
    _roomCode = null;
    _roomUsers.clear();
  }

  void sendOffer({required String to, required Map<String, dynamic> offer}) {
    _socket?.emit('webrtc-offer', {'to': to, 'offer': offer});
  }

  void sendAnswer({required String to, required Map<String, dynamic> answer}) {
    _socket?.emit('webrtc-answer', {'to': to, 'answer': answer});
  }

  void sendIceCandidate({required String to, required Map<String, dynamic> candidate}) {
    _socket?.emit('ice-candidate', {'to': to, 'candidate': candidate});
  }

  void sendEncryptedMessage({
    required String to,
    required String payload,
    String? demoPlaintext,
  }) {
    if (_socket == null || !_socket!.connected) return;
    _socket!.emit('e2e-message', {
      'to': to,
      'payload': payload,
      if (demoPlaintext != null) 'demoPlaintext': demoPlaintext,
    });
  }

  Future<void> disconnect() async {
    AppLogger.i('Signaling', 'disconnect');
    _token = null;
    _authCompleter = null;
    _roomCode = null;
    _socket?.dispose();
    _socket = null;
    _roomUsers.clear();
  }
}
