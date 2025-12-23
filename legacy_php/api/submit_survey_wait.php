await http.post(
  Uri.parse('https://yourdomain.com/api.php?action=submit_survey'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({
    'beneficiary_id': 1,
    'question': 'Did you receive food support?',
    'response': 'Yes',
  }),
);
