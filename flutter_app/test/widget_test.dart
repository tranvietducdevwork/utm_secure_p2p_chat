import 'package:flutter_test/flutter_test.dart';
import 'package:secure_p2p_chat/features/auth/login_screen.dart';
import 'package:flutter/material.dart';

void main() {
  testWidgets('Login screen renders', (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: LoginScreen()),
    );
    await tester.pump();
    expect(find.text('Secure P2P Chat'), findsOneWidget);
  });
}
