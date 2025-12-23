class BiometricScreen extends StatelessWidget {
  void authenticate() async {
    final auth = LocalAuthentication();
    final didAuth = await auth.authenticate(localizedReason: 'Scan fingerprint');
    print(didAuth ? 'Authenticated' : 'Failed');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(child: ElevatedButton(onPressed: authenticate, child: Text('Scan Fingerprint')))
    );
  }
}
