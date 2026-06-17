import 'dart:async';

import 'package:cryptography/cryptography.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_webrtc/flutter_webrtc.dart';

import '../../config/app_config.dart';
import '../../core/crypto/e2e_crypto.dart';
import '../../services/signaling_service.dart';

enum PeerConnectionState { disconnected, connecting, connected, failed }

class PeerConnectionManager {
  PeerConnectionManager({
    required this.signaling,
    required this.localUsername,
    required this.localKeyPair,
    required this.remoteUsername,
    required this.remotePublicKeyBase64,
    required this.isInitiator,
  });

  final SignalingService signaling;
  final String localUsername;
  final SimpleKeyPair localKeyPair;
  final String remoteUsername;
  final String remotePublicKeyBase64;
  final bool isInitiator;

  RTCPeerConnection? _peerConnection;
  RTCDataChannel? _dataChannel;
  SecretKey? _sharedSecret;
  final List<Map<String, dynamic>> _pendingCandidates = [];
  bool _remoteDescriptionSet = false;

  final _messageController = StreamController<String>.broadcast();
  Stream<String> get messages => _messageController.stream;

  final _stateController = StreamController<PeerConnectionState>.broadcast();
  Stream<PeerConnectionState> get connectionState => _stateController.stream;

  PeerConnectionState _state = PeerConnectionState.disconnected;
  PeerConnectionState get state => _state;

  void _setState(PeerConnectionState newState) {
    _state = newState;
    _stateController.add(newState);
  }

  Future<void> initialize() async {
    _setState(PeerConnectionState.connecting);

    _sharedSecret = await E2ECrypto.deriveSharedSecret(
      localKeyPair: localKeyPair,
      remotePublicKeyBase64: remotePublicKeyBase64,
    );

    _peerConnection = await createPeerConnection({
      'iceServers': AppConfig.stunServers,
      'sdpSemantics': 'unified-plan',
      'iceCandidatePoolSize': 10,
      'bundlePolicy': 'max-bundle',
      'rtcpMuxPolicy': 'require',
    });

    _peerConnection!.onIceCandidate = (candidate) {
      signaling.sendIceCandidate(
        to: remoteUsername,
        candidate: candidate.toMap(),
      );
    };

    _peerConnection!.onConnectionState = (state) {
      if (state == RTCPeerConnectionState.RTCPeerConnectionStateConnected) {
        _setState(PeerConnectionState.connected);
      } else if (state == RTCPeerConnectionState.RTCPeerConnectionStateFailed ||
          state == RTCPeerConnectionState.RTCPeerConnectionStateDisconnected) {
        _setState(PeerConnectionState.failed);
      }
    };

    _peerConnection!.onDataChannel = (channel) {
      _setupDataChannel(channel);
    };

    if (isInitiator) {
      final channel = await _peerConnection!.createDataChannel(
        'chat',
        RTCDataChannelInit()..ordered = true,
      );
      _setupDataChannel(channel);
      final offer = await _peerConnection!.createOffer();
      await _peerConnection!.setLocalDescription(offer);
      signaling.sendOffer(to: remoteUsername, offer: offer.toMap());
    }
  }

  void _setupDataChannel(RTCDataChannel channel) {
    _dataChannel = channel;
    channel.onMessage = (message) async {
      if (message.isBinary) return;
      try {
        final decrypted = await E2ECrypto.decryptMessage(
          sharedSecret: _sharedSecret!,
          encryptedPayload: message.text,
        );
        _messageController.add(decrypted);
      } catch (e) {
        debugPrint('Decrypt error: $e');
      }
    };
    channel.onDataChannelState = (state) {
      if (state == RTCDataChannelState.RTCDataChannelOpen) {
        _setState(PeerConnectionState.connected);
      }
    };
  }

  Future<void> handleOffer(Map<String, dynamic> offerMap) async {
    if (_peerConnection == null) await initialize();
    final offer = RTCSessionDescription(offerMap['sdp'], offerMap['type']);
    await _peerConnection!.setRemoteDescription(offer);
    _remoteDescriptionSet = true;
    await _flushPendingCandidates();
    final answer = await _peerConnection!.createAnswer();
    await _peerConnection!.setLocalDescription(answer);
    signaling.sendAnswer(to: remoteUsername, answer: answer.toMap());
  }

  Future<void> handleAnswer(Map<String, dynamic> answerMap) async {
    final answer = RTCSessionDescription(answerMap['sdp'], answerMap['type']);
    await _peerConnection?.setRemoteDescription(answer);
    _remoteDescriptionSet = true;
    await _flushPendingCandidates();
  }

  Future<void> handleIceCandidate(Map<String, dynamic> candidateMap) async {
    if (!_remoteDescriptionSet) {
      _pendingCandidates.add(candidateMap);
      return;
    }
    await _addCandidate(candidateMap);
  }

  Future<void> _flushPendingCandidates() async {
    final pending = List<Map<String, dynamic>>.from(_pendingCandidates);
    _pendingCandidates.clear();
    for (final c in pending) {
      await _addCandidate(c);
    }
  }

  Future<void> _addCandidate(Map<String, dynamic> candidateMap) async {
    final candidate = RTCIceCandidate(
      candidateMap['candidate'],
      candidateMap['sdpMid'],
      candidateMap['sdpMLineIndex'],
    );
    await _peerConnection?.addCandidate(candidate);
  }

  Future<bool> sendMessage(String plaintext) async {
    if (_dataChannel == null || _sharedSecret == null) return false;
    if (_dataChannel!.state != RTCDataChannelState.RTCDataChannelOpen) {
      return false;
    }
    final encrypted = await E2ECrypto.encryptMessage(
      sharedSecret: _sharedSecret!,
      plaintext: plaintext,
    );
    _dataChannel!.send(RTCDataChannelMessage(encrypted));
    return true;
  }

  Future<void> dispose() async {
    await _dataChannel?.close();
    await _peerConnection?.close();
    await _messageController.close();
    await _stateController.close();
  }
}
