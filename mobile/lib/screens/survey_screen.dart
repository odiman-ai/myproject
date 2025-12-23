class SurveyScreen extends StatelessWidget {
  final question1 = TextEditingController();

  void submitSurvey() async {
    final response = await ApiService.post('/submit_survey.php', {
      'beneficiary_id': '1',
      'responses': {'q1': question1.text}
    });
    print(response);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(children: [
        TextField(controller: question1),
        ElevatedButton(onPressed: submitSurvey, child: Text('Submit Survey'))
      ]),
    );
  }
}
