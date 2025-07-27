from rest_framework import serializers
from django.utils import timezone
from app.teacher.models import HomeworkSubmission

class TeacherHomeworkSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    lesson_date = serializers.DateField(source="lesson.date")
    lesson_title = serializers.CharField(source="lesson.course.name")

    class Meta:
        model = HomeworkSubmission
        fields = [
            "id", "student_name", "lesson_date", "lesson_title",
            "comment", "link", "file", "submitted_at",
            "score", "teacher_comment", "reviewed"
        ]

    def get_student_name(self, obj):
        return obj.student.get_full_name()


class TeacherHomeworkCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeworkSubmission
        fields = ["score", "teacher_comment", "reviewed"]

    def update(self, instance, validated_data):
        instance.score = validated_data.get("score", "")
        instance.teacher_comment = validated_data.get("teacher_comment", "")
        instance.reviewed = validated_data.get("reviewed", True)
        instance.reviewed_at = timezone.now()
        instance.reviewed_by = self.context["request"].user
        instance.save()
        return instance
