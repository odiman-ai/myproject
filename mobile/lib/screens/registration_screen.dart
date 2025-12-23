class RegistrationScreen extends StatelessWidget {
  final name = TextEditingController();
  final dob = TextEditingController();
  final location = TextEditingController();

  void register() async {
    final data = {
      'name': name.text,
      'dob': dob.text,
      'location': location.text,
    };
    final response = await ApiService.post('/create_beneficiary.php', data);
    print(response);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(children: [
        TextField(controller: name),
        TextField(controller: dob),
        TextField(controller: location),
        ElevatedButton(onPressed: register, child: Text('Register'))
      ]),
    );
  }
}
