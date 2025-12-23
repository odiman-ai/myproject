final response = await http.post(
  Uri.parse('https://yourdomain.com/api/submit_survey.php'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({
    'beneficiary_id': 1,
    'question': 'Did you receive food support?',
    'response': 'Yes',
  }),
);

final result = jsonDecode(response.body);
print(result['message']);
