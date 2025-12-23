class EligibilityScreen extends StatelessWidget {
  final beneficiaryId = TextEditingController();

  void checkEligibility() async {
    final response = await ApiService.get('/check_eligibility.php?id=${beneficiaryId.text}');
    print(response);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(children: [
        TextField(controller: beneficiaryId),
        ElevatedButton(onPressed: checkEligibility, child: Text('Check Eligibility'))
      ]),
    );
  }
}
