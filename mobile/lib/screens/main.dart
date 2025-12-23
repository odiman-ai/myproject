import 'package:flutter/material.dart';
import 'screens/login_screen.dart';
import 'screens/registration_screen.dart';
import 'screens/eligibility_screen.dart';
import 'screens/attendance_screen.dart';
import 'screens/survey_screen.dart';
import 'screens/biometric_screen.dart';

void main() => runApp(BeneficiaryApp());

class BeneficiaryApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Beneficiary App',
      theme: ThemeData(primarySwatch: Colors.teal),
      initialRoute: '/',
      routes: {
        '/': (context) => LoginScreen(),
        '/registration': (context) => RegistrationScreen(),
        '/eligibility': (context) => EligibilityScreen(),
        '/attendance': (context) => AttendanceScreen(),
        '/survey': (context) => SurveyScreen(),
        '/biometric': (context) => BiometricScreen(),
      },
    );
  }
}
