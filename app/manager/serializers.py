from rest_framework import serializers
from .models import StudentRequest, Payment, PaymentReminder, Expense, TeacherRate, TeacherBonus
from app.users.models import CustomUser
from app.students.models import Lesson, Attendance, Homework
from app.students.serializers import LessonSerializer, HomeworkSerializer
from rest_framework import serializers
from django.db.models import Count

class StudentManagerRequestSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source="course.name", read_only=True)
    assigned_name = serializers.CharField(source="assigned_to.get_full_name", read_only=True)

    class Meta:
        model = StudentRequest
        fields = [
            "id", "full_name", "phone", "email", "course", "course_name",
            "message", "status", "assigned_to", "assigned_name", "source",
            "created_at", "scheduled_at"
        ]
        ref_name = "StudentManagerRequestSerializer"

    def create(self, validated_data):
        if 'assigned_to' not in validated_data:
            validated_data['assigned_to'] = self.context['request'].user
        return super().create(validated_data)

class StudentShortSerializer(serializers.ModelSerializer):
    course = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()

    def get_course(self, obj):
        enrollment = obj.enrollments.first()
        return enrollment.course.name if enrollment else ""

    def get_group(self, obj):
        enrollment = obj.enrollments.first()
        return enrollment.group_name if enrollment else ""

    class Meta:
        model = CustomUser
        fields = ("id", "first_name", "last_name", "username", "phone", "telegram", "course", "group")

class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", "phone", "telegram", "username", "password")

class PaymentSerializers(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.get_full_name", read_only=True)
    course_name = serializers.CharField(source="course.name", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id", "student", "student_name", "course", "course_name",
            "amount_cash", "amount_transfer", "amount_online",
            "total_amount", "comment", "status", "date"
        ]
        ref_name = "ManagerPaymentSerializer"

class PaymentReminderSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.get_full_name", read_only=True)
    course_name = serializers.CharField(source="course.name", read_only=True)

    class Meta:
        model = PaymentReminder
        fields = ["id", "student", "student_name", "course", "course_name", "message", "amount", "due_date", "created_at"]

class FinancialSummarySerializer(serializers.Serializer):
    revenue = serializers.IntegerField()
    expenses = serializers.IntegerField()
    profit = serializers.IntegerField()

class TeacherReportSerializer(serializers.Serializer):
    teacher_id = serializers.IntegerField()
    teacher_name = serializers.CharField()
    lesson_count = serializers.IntegerField()
    rate = serializers.IntegerField()
    salary = serializers.IntegerField()
    bonus = serializers.IntegerField()
    total_payout = serializers.IntegerField()
