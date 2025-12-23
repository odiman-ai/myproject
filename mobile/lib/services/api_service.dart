import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  static const baseUrl = 'http://192.168.0.101/myproject';

  static Future<Map<String, dynamic>> post(String endpoint, Map data) async {
    final res = await http.post(Uri.parse('$baseUrl$endpoint'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(data));
    return jsonDecode(res.body);
  }

  static Future<Map<String, dynamic>> get(String endpoint) async {
    final res = await http.get(Uri.parse('$baseUrl$endpoint'));
    return jsonDecode(res.body);
  }
}
