class AttendanceScreen extends StatelessWidget {
  final beneficiaryId = TextEditingController();

  void markAttendance() async {
    final response = await ApiService.post('/submit_attendance.php', {
      'beneficiary_id': beneficiaryId.text,
      'timestamp': DateTime.now().toIso8601String()
    });
    print(response);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(children: [
        TextField(controller: beneficiaryId),
        ElevatedButton(onPressed: markAttendance, child: Text('Mark Attendance'))
      ]),
    );
  }
}
