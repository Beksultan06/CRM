from rest_framework import serializers
from django.db.models import Sum, Avg, Q
from app.users.models import CustomUser
from app.students.models import Lesson, Homework, Attendance, Curriculum
from app.manager.models import Payment
from .models import Group, HomeworkSubmission

class GroupSerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ["id", "name", "teacher", "teacher_name", "status", "format", "age_group", "created_at"]

    def get_teacher_name(self, obj):
        return obj.teacher.get_full_name() if obj.teacher else ""

class GroupStudentSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    paid = serializers.SerializerMethodField()
    debt = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ["id", "first_name", "last_name", "status", "paid", "debt"]

    def get_status(self, obj):
        return "Активный" if obj.is_active else "Не активный"

    def get_paid(self, obj):
        return obj.payments.filter(status="paid").aggregate(total=Sum("total_amount"))['total'] or 0

    def get_debt(self, obj):
        total = self.get_paid(obj)
        return max(14000 - total, 0)

class GroupCurriculumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curriculum
        fields = ["month_number", "title", "lessons_outline"]

class HomeworkSubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    lesson_title = serializers.SerializerMethodField()

    class Meta:
        model = HomeworkSubmission
        fields = ["id", "student", "student_name", "lesson", "lesson_title", "comment", "link", "file", "submitted_at", "score", "teacher_comment", "reviewed", "reviewed_at"]

    def get_student_name(self, obj):
        return obj.student.get_full_name()

    def get_lesson_title(self, obj):
        return f"{obj.lesson.group_name} {obj.lesson.date}"

class HomeworkReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeworkSubmission
        fields = ["score", "teacher_comment", "reviewed"]

    def update(self, instance, validated_data):
        instance.reviewed = True
        instance.reviewed_at = timezone.now()
        instance.reviewed_by = self.context['request'].user
        return super().update(instance, validated_data)

class GroupAttendanceSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source="lesson.group_name")
    class Meta:
        model = Attendance
        fields = ["student", "lesson", "lesson_title", "attended"]

class GroupStatisticSerializer(serializers.Serializer):
    attendance_rate = serializers.FloatField()
    avg_homework_score = serializers.FloatField()