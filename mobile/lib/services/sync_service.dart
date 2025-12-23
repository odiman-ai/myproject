import 'dart:convert';
import 'package:http/http.dart' as http;

class SyncService {
  final String baseUrl;

  SyncService({required this.baseUrl});

  Future<void> syncAttendance(Map<String, dynamic> attendanceData) async {
    final response = await http.post(
      Uri.parse('$baseUrl/attendance/sync'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(attendanceData),
    );
    if (response.statusCode != 200) {
      throw Exception('Failed to sync attendance');
    }
  }
}
