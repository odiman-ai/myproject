import 'package:flutter/material.dart';
import '../models/beneficiary.dart';

class BeneficiaryProvider with ChangeNotifier {
  List<Beneficiary> _beneficiaries = [];

  List<Beneficiary> get beneficiaries => _beneficiaries;

  void addBeneficiary(Beneficiary beneficiary) {
    _beneficiaries.add(beneficiary);
    notifyListeners();
  }

  void removeBeneficiary(String id) {
    _beneficiaries.removeWhere((b) => b.id == id);
    notifyListeners();
  }
}
