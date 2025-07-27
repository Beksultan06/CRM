from rest_framework import serializers
from app.teacher.models import HomeworkSubmission

class HomeworkReviewSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.get_full_name", read_only=True)
    lesson_date = serializers.DateField(source="lesson.date", read_only=True)

    class Meta:
        model = HomeworkSubmission
        fields = [
            "id", "student", "student_name", "lesson", "lesson_date",
            "comment", "link", "file", "score",
            "teacher_comment", "reviewed", "reviewed_at"
        ]
        read_only_fields = ["student", "lesson", "link", "file", "comment", "reviewed_at"]
