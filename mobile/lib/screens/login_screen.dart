class LoginScreen extends StatelessWidget {
  final TextEditingController username = TextEditingController();
  final TextEditingController password = TextEditingController();

  void login(BuildContext context) async {
    final response = await AuthService.login(username.text, password.text);
    if (response['status'] == 'success') {
      Navigator.pushNamed(context, '/registration');
    } else {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(response['message'])));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(children: [
        TextField(controller: username),
        TextField(controller: password, obscureText: true),
        ElevatedButton(onPressed: () => login(context), child: Text('Login'))
      ]),
    );
  }
}
