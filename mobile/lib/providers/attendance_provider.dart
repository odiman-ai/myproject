import 'package:flutter/material.dart';
import '../models/attendance.dart';

class AttendanceProvider with ChangeNotifier {
  List<Attendance> _records = [];

  List<Attendance> get records => _records;

  void addRecord(Attendance record) {
    _records.add(record);
    notifyListeners();
  }

  void clearRecords() {
    _records.clear();
    notifyListeners();
  }
}
