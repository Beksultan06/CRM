from rest_framework import serializers
from app.users.models import CustomUser
from app.administator.models import TeacherSalary
from app.students.models import Enrollment, Lesson
from django.db.models.functions import TruncMonth
from django.db.models import Count
from datetime import datetime

class TeacherSalarySerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherSalary
        fields = ["salary_type", "amount"]

class TeacherSerializer(serializers.ModelSerializer):
    salary = TeacherSalarySerializer(source="teachersalary", read_only=True)
    group = serializers.CharField(source="group.name", read_only=True)
    direction = serializers.CharField(source="group.course.name", read_only=True)
    student_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            "id", "first_name", "last_name", "telegram", "phone", "username", 
            "group", "direction", "student_count", "salary"
        ]

    def get_student_count(self, obj):
        return obj.group.students.count() if obj.group else 0


class TeacherStudentSerializer(serializers.ModelSerializer):
    group = serializers.CharField(source="group.name")
    course = serializers.CharField(source="course.name")
    status = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = ("student", "group", "course", "status")

    def get_status(self, obj):
        return "Активный"

class TeacherLessonSerializer(serializers.ModelSerializer):
    course = serializers.CharField(source="course.name")
    group = serializers.CharField(source="group.name")
    classroom = serializers.CharField(source="classroom.label")

    class Meta:
        model = Lesson
        fields = ["id", "date", "start_time", "end_time", "course", "group", "classroom"]

class TeacherSalarySummarySerializer(serializers.Serializer):
    month = serializers.CharField()
    lesson_count = serializers.IntegerField()
    rate = serializers.IntegerField()
    bonus = serializers.IntegerField()
    total = serializers.IntegerField()

    def to_representation(self, instance):
        teacher_id = self.context.get("teacher_id")

        salary = TeacherSalary.objects.filter(teacher_id=teacher_id).first()
        salary_type = salary.salary_type if salary else "hourly"
        rate = salary.amount if salary else 0

        lessons = (
            Lesson.objects.filter(teacher_id=teacher_id)
            .annotate(month=TruncMonth("date"))
            .values("month")
            .annotate(lesson_count=Count("id"))
            .order_by("-month")
        )

        bonuses = {
            b.month.strftime("%Y-%m"): b.amount
            for b in TeacherBonus.objects.filter(teacher_id=teacher_id)
        }

        result = []
        for entry in lessons:
            month = entry["month"].strftime("%Y-%m")
            lesson_count = entry["lesson_count"]
            bonus = bonuses.get(month, 0)

            if salary_type == "fixed":
                total = rate + bonus
            else: 
                total = lesson_count * rate + bonus

            result.append({
                "month": month,
                "lesson_count": lesson_count,
                "rate": rate,
                "bonus": bonus,
                "total": total
            })

        return {"summary": result} 



class TeacherLessonSerializer(serializers.ModelSerializer):
    course = serializers.CharField(source="course.name")
    classroom = serializers.CharField(source="classroom.label")

    class Meta:
        model = Lesson
        fields = [
            "id", "date", "start_time", "end_time",
            "course", "group_name", "classroom"
        ]

class TeacherCalendarLessonSerializer(serializers.ModelSerializer):
    course = serializers.CharField(source="course.name")
    group = serializers.CharField(source="group.name")
    classroom = serializers.CharField(source="classroom.label")

    class Meta:
        model = Lesson
        fields = ["id", "date", "start_time", "end_time", "course", "group", "classroom"]