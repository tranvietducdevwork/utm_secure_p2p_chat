import 'dart:async';

import 'package:cryptography/cryptography.dart';
import 'package:flutter/foundation.dart';

import '../../config/app_config.dart';
import '../../core/crypto/e2e_crypto.dart';
import '../../core/webrtc/peer_connection_manager.dart';
import '../../services/signaling_service.dart';

enum ChatTransportMode { connecting, p2p, relay, failed }

class ChatSession {
  ChatSession({
    required this.signaling,
    required this.localKeyPair,
    required this.localUsername,
    required this.remoteUsername,
    required this.remotePublicKeyBase64,
    required this.isInitiator,
    this.sendDemoPlaintext = false,
    this.onIncomingMessage,
  });

  final SignalingService signaling;
  final SimpleKeyPair localKeyPair;
  final String localUsername;
  final String remoteUsername;
  final String remotePublicKeyBase64;
  final bool isInitiator;
  final bool sendDemoPlaintext;
  final void Function(String plaintext)? onIncomingMessage;

  PeerConnectionManager? _p2p;
  SecretKey? _sharedSecret;
  Timer? _fallbackTimer;

  final _modeController = StreamController<ChatTransportMode>.broadcast();
  Stream<ChatTransportMode> get modeStream => _modeController.stream;

  ChatTransportMode _mode = ChatTransportMode.connecting;
  ChatTransportMode get mode => _mode;

  void _setMode(ChatTransportMode mode) {
    _mode = mode;
    _modeController.add(mode);
  }

  Future<void> start() async {
    if (remotePublicKeyBase64.isEmpty) {
      throw Exception('Thiếu public key của $remoteUsername');
    }

    _sharedSecret = await E2ECrypto.deriveSharedSecret(
      localKeyPair: localKeyPair,
      remotePublicKeyBase64: remotePublicKeyBase64,
    );

    // Emulator / NAT: bật relay ngay để chat được, thử P2P song song
    _setMode(ChatTransportMode.relay);

    _p2p = PeerConnectionManager(
      signaling: signaling,
      localUsername: localUsername,
      localKeyPair: localKeyPair,
      remoteUsername: remoteUsername,
      remotePublicKeyBase64: remotePublicKeyBase64,
      isInitiator: isInitiator,
    );

    _p2p!.messages.listen((text) {
      onIncomingMessage?.call(text);
    });

    _p2p!.connectionState.listen((state) {
      if (state == PeerConnectionState.connected) {
        _fallbackTimer?.cancel();
        _setMode(ChatTransportMode.p2p);
      }
    });

    unawaited(_p2p!.initialize().catchError((e) {
      debugPrint('P2P init error (OK on emulator): $e');
    }));

    _fallbackTimer = Timer(AppConfig.p2pConnectTimeout, () {
      if (_mode != ChatTransportMode.p2p) {
        _setMode(ChatTransportMode.relay);
      }
    });
  }

  Future<void> handleOffer(Map<String, dynamic> offer) async {
    await _p2p?.handleOffer(offer);
  }

  Future<void> handleAnswer(Map<String, dynamic> answer) async {
    await _p2p?.handleAnswer(answer);
  }

  Future<void> handleIceCandidate(Map<String, dynamic> candidate) async {
    await _p2p?.handleIceCandidate(candidate);
  }

  Future<void> handleRelayPayload(String encryptedPayload) async {
    if (_sharedSecret == null) return;
    try {
      final text = await E2ECrypto.decryptMessage(
        sharedSecret: _sharedSecret!,
        encryptedPayload: encryptedPayload,
      );
      debugPrint('Received relay message from $remoteUsername: $text');
      onIncomingMessage?.call(text);
    } catch (e) {
      debugPrint('Relay decrypt error from $remoteUsername: $e');
    }
  }

  Future<bool> sendMessage(String plaintext) async {
    if (_sharedSecret == null) return false;

    final encrypted = await E2ECrypto.encryptMessage(
      sharedSecret: _sharedSecret!,
      plaintext: plaintext,
    );

    if (_mode == ChatTransportMode.p2p) {
      final sent = await _p2p!.sendMessage(plaintext);
      if (sent) return true;
      _setMode(ChatTransportMode.relay);
    }

    signaling.sendEncryptedMessage(
      to: remoteUsername,
      payload: encrypted,
      demoPlaintext: sendDemoPlaintext ? plaintext : null,
    );
    debugPrint('Sent relay message to $remoteUsername');
    return true;
  }

  bool get canSend =>
      _mode == ChatTransportMode.p2p ||
      _mode == ChatTransportMode.relay ||
      _mode == ChatTransportMode.connecting;

  Future<void> dispose() async {
    _fallbackTimer?.cancel();
    await _p2p?.dispose();
    await _modeController.close();
  }
}
