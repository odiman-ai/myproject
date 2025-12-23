import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';
import 'package:myproject/widgets/loading_spinner.dart';

void main() {
  testWidgets('LoadingSpinner shows CircularProgressIndicator',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: LoadingSpinner(),
      ),
    );

    expect(find.byType(CircularProgressIndicator), findsOneWidget);
  });
}
