import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';
import 'package:myproject/widgets/form_field.dart';

void main() {
  testWidgets('FormFieldWidget displays label and accepts input',
      (WidgetTester tester) async {
    final controller = TextEditingController();

    await tester.pumpWidget(
      MaterialApp(
        home: FormFieldWidget(
          label: 'Name',
          controller: controller,
        ),
      ),
    );

    expect(find.text('Name'), findsOneWidget);

    await tester.enterText(find.byType(TextFormField), 'Simon');
    expect(controller.text, 'Simon');
  });
}
