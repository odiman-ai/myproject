class Survey {
  final String id;
  final String surveyCode;
  final String title;
  final List<Map<String, dynamic>> questions;

  Survey({
    required this.id,
    required this.surveyCode,
    required this.title,
    required this.questions,
  });

  factory Survey.fromJson(Map<String, dynamic> json) {
    return Survey(
      id: json['id'],
      surveyCode: json['survey_code'],
      title: json['title'],
      questions: List<Map<String, dynamic>>.from(json['questions']),
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'survey_code': surveyCode,
        'title': title,
        'questions': questions,
      };
}
