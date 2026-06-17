import 'dart:convert';
import 'dart:typed_data';

import 'package:cryptography/cryptography.dart';

/// End-to-end encryption using X25519 key exchange + AES-GCM.
class E2ECrypto {
  E2ECrypto._();

  static final _algorithm = X25519();
  static final _aesGcm = AesGcm.with256bits();
  static final _hkdf = Hkdf(hmac: Hmac.sha256(), outputLength: 32);

  static Future<SimpleKeyPair> generateKeyPair() {
    return _algorithm.newKeyPair();
  }

  static Future<String> publicKeyToBase64(SimplePublicKey publicKey) async {
    return base64Encode(publicKey.bytes);
  }

  static SimplePublicKey publicKeyFromBase64(String base64Key) {
    return SimplePublicKey(
      base64Decode(base64Key),
      type: KeyPairType.x25519,
    );
  }

  static Future<String> privateKeyToBase64(SimpleKeyPair keyPair) async {
    final bytes = await keyPair.extractPrivateKeyBytes();
    return base64Encode(bytes);
  }

  static Future<SimpleKeyPair> keyPairFromPrivateBase64(String base64Key) async {
    final privateBytes = base64Decode(base64Key);
    return _algorithm.newKeyPairFromSeed(privateBytes);
  }

  static Future<SecretKey> deriveSharedSecret({
    required SimpleKeyPair localKeyPair,
    required String remotePublicKeyBase64,
  }) async {
    final remotePublicKey = publicKeyFromBase64(remotePublicKeyBase64);
    final rawSecret = await _algorithm.sharedSecretKey(
      keyPair: localKeyPair,
      remotePublicKey: remotePublicKey,
    );
    final rawBytes = await rawSecret.extractBytes();
    return _hkdf.deriveKey(
      secretKey: SecretKey(rawBytes),
      nonce: Uint8List.fromList('secure-p2p-chat'.codeUnits),
      info: utf8.encode('e2e-aes-gcm'),
    );
  }

  static Future<String> encryptMessage({
    required SecretKey sharedSecret,
    required String plaintext,
  }) async {
    final nonce = _aesGcm.newNonce();
    final secretBox = await _aesGcm.encrypt(
      utf8.encode(plaintext),
      secretKey: sharedSecret,
      nonce: nonce,
    );
    final payload = <String, dynamic>{
      'n': base64Encode(nonce),
      'c': base64Encode(secretBox.cipherText),
      'm': base64Encode(secretBox.mac.bytes),
    };
    return jsonEncode(payload);
  }

  static Future<String> decryptMessage({
    required SecretKey sharedSecret,
    required String encryptedPayload,
  }) async {
    final map = jsonDecode(encryptedPayload) as Map<String, dynamic>;
    final nonce = base64Decode(map['n'] as String);
    final cipherText = base64Decode(map['c'] as String);
    final mac = Mac(base64Decode(map['m'] as String));
    final secretBox = SecretBox(cipherText, nonce: nonce, mac: mac);
    final clearBytes = await _aesGcm.decrypt(secretBox, secretKey: sharedSecret);
    return utf8.decode(clearBytes);
  }
}
