await http.post(
  Uri.parse('https://yourdomain.com/api.php?action=register_beneficiary'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({
    'beneficiary_code': 'BNF005',
    'first_name': 'Simon',
    'last_name': 'Akalees',
    'date_of_birth': '1985-07-10',
    'gender': 'Male',
    'village': 'Yenglemi',
    'parish': 'Yenglemi Parish',
    'subcounty': 'Karenga SC',
    'district': 'Karenga',
    'contact_phone': '0701111111',
    'disability_status': 'None',
    'vulnerability_category': 'Elderly',
    'relationship_to_household_head': 'Self',
    'marital_status': 'Married',
    'status': 'active',
    'created_by': 1
  }),
);
