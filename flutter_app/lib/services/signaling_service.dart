import 'dart:async';

import 'package:socket_io_client/socket_io_client.dart' as io;

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
  SignalingCallback? onWebRtcOffer;
  SignalingCallback? onWebRtcAnswer;
  SignalingCallback? onIceCandidate;
  SignalingCallback? onEncryptedMessage;

  void _authenticate() {
    final token = _token;
    if (token != null && _socket != null) {
      _socket!.emit('authenticate', {'token': token});
    }
  }

  void _setRoomUsers(List<ChatUser> users) {
    _roomUsers
      ..clear()
      ..addAll(users);
    onRoomUsersChanged?.call(roomUsers);
  }

  void _attachHandlers() {
    _socket!
      ..onConnect((_) => _authenticate())
      ..on('authenticated', (_) {
        _authCompleter?.complete();
        _authCompleter = null;
        if (_roomCode != null) {
          _socket!.emit('join-room', {'roomCode': _roomCode});
        }
      })
      ..on('room-joined', (data) {
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
        final map = _asStringMap(data);
        _roomCode = map['roomCode'] as String? ?? _roomCode;
        final users = (map['users'] as List<dynamic>? ?? [])
            .map((e) => ChatUser.fromJson(_asStringMap(e)))
            .toList();
        _setRoomUsers(users);
      })
      ..on('user-joined-room', (data) {
        final map = _asStringMap(data);
        final user = ChatUser.fromJson(_asStringMap(map['user']));
        _roomCode = map['roomCode'] as String? ?? _roomCode;
        _roomUsers.removeWhere((u) => u.username == user.username);
        _roomUsers.add(user);
        onRoomUsersChanged?.call(roomUsers);
      })
      ..on('user-left-room', (data) {
        final map = _asStringMap(data);
        final username = map['username'] as String? ?? '';
        _roomUsers.removeWhere((u) => u.username == username);
        onRoomUsersChanged?.call(roomUsers);
      })
      ..on('room-left', (_) {
        _roomCode = null;
        _roomUsers.clear();
        onRoomUsersChanged?.call(roomUsers);
      })
      ..on('room-error', (data) {
        final map = _asStringMap(data);
        onRoomError?.call(map['message'] as String? ?? 'Không thể vào phòng');
      })
      ..on('webrtc-offer', (data) => onWebRtcOffer?.call(_asStringMap(data)))
      ..on('webrtc-answer', (data) => onWebRtcAnswer?.call(_asStringMap(data)))
      ..on('ice-candidate', (data) => onIceCandidate?.call(_asStringMap(data)))
      ..on('e2e-message', (data) => onEncryptedMessage?.call(_asStringMap(data)));
  }

  Future<void> connect(String token) async {
    _token = token;
    await disconnect();

    _authCompleter = Completer<void>();
    _socket = io.io(
      serverUrl,
      io.OptionBuilder()
          .setTransports(['websocket'])
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
      await _authCompleter!.future.timeout(const Duration(seconds: 8));
    } catch (_) {}
  }

  Future<void> joinRoom(String roomCode) async {
    if (_socket == null || !_socket!.connected) {
      throw Exception('Chưa kết nối server');
    }

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

    await completer.future.timeout(const Duration(seconds: 8));
    _socket!.off('room-joined', onJoined);
    _socket!.off('room-error', onError);
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

  void sendEncryptedMessage({required String to, required String payload}) {
    if (_socket == null || !_socket!.connected) return;
    _socket!.emit('e2e-message', {'to': to, 'payload': payload});
  }

  Future<void> disconnect() async {
    _token = null;
    _authCompleter = null;
    _roomCode = null;
    _socket?.dispose();
    _socket = null;
    _roomUsers.clear();
  }
}
