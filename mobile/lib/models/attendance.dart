class Attendance {
  final String id;
  final String participantId;
  final String activityId;
  final DateTime checkInTime;
  final String verificationMethod;

  Attendance({
    required this.id,
    required this.participantId,
    required this.activityId,
    required this.checkInTime,
    required this.verificationMethod,
  });

  factory Attendance.fromJson(Map<String, dynamic> json) {
    return Attendance(
      id: json['id'],
      participantId: json['participant_id'],
      activityId: json['activity_id'],
      checkInTime: DateTime.parse(json['check_in_time']),
      verificationMethod: json['verification_method'],
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'participant_id': participantId,
        'activity_id': activityId,
        'check_in_time': checkInTime.toIso8601String(),
        'verification_method': verificationMethod,
      };
}
