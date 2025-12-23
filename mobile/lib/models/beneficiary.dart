// File: mobile/lib/models/beneficiary.dart

import 'dart:convert';

class Beneficiary {
  final String id;
  final String participantCode;
  final String firstName;
  final String lastName;
  final DateTime dateOfBirth;
  final String gender;
  final String phoneNumber;
  final String? nationalId;
  final String status;
  final int vulnerabilityScore;
  final String? photoUrl;
  final String? qrCodeUrl;
  final double? latitude;
  final double? longitude;

  Beneficiary({
    required this.id,
    required this.participantCode,
    required this.firstName,
    required this.lastName,
    required this.dateOfBirth,
    required this.gender,
    required this.phoneNumber,
    this.nationalId,
    required this.status,
    required this.vulnerabilityScore,
    this.photoUrl,
    this.qrCodeUrl,
    this.latitude,
    this.longitude,
  });

  factory Beneficiary.fromJson(Map<String, dynamic> json) {
    return Beneficiary(
      id: json['id'],
      participantCode: json['participant_code'],
      firstName: json['first_name'],
      lastName: json['last_name'],
      dateOfBirth: DateTime.parse(json['date_of_birth']),
      gender: json['gender'],
      phoneNumber: json['phone_number'],
      nationalId: json['national_id'],
      status: json['status'],
      vulnerabilityScore: json['vulnerability_score'] ?? 0,
      photoUrl: json['photo_url'],
      qrCodeUrl: json['qr_code_url'],
      latitude: json['latitude'],
      longitude: json['longitude'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'participant_code': participantCode,
      'first_name': firstName,
      'last_name': lastName,
      'date_of_birth': dateOfBirth.toIso8601String(),
      'gender': gender,
      'phone_number': phoneNumber,
      'national_id': nationalId,
      'status': status,
      'vulnerability_score': vulnerabilityScore,
      'photo_url': photoUrl,
      'qr_code_url': qrCodeUrl,
      'latitude': latitude,
      'longitude': longitude,
    };
  }

  String get fullName => '$firstName $lastName';
}
