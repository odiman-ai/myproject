import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';
import 'package:myproject/widgets/custom_button.dart';

void main() {
  testWidgets('CustomButton displays label and triggers callback',
      (WidgetTester tester) async {
    bool pressed = false;

    await tester.pumpWidget(
      MaterialApp(
        home: CustomButton(
          label: 'Submit',
          onPressed: () {
            pressed = true;
          },
        ),
      ),
    );

    expect(find.text('Submit'), findsOneWidget);

    await tester.tap(find.text('Submit'));
    await tester.pump();

    expect(pressed, true);
  });
}
