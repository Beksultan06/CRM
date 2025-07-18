from rest_framework import serializers
from django.utils import formats
from app.students.models import *

class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = ("label",)

class LessonSerializer(serializers.ModelSerializer):
    course = serializers.StringRelatedField()
    teacher = serializers.StringRelatedField()
    classroom = ClassroomSerializer()
    start_time = serializers.TimeField(format="%H:%M")
    end_time = serializers.TimeField(format="%H:%M")

    class Meta:
        model = Lesson
        fields = (
            "id",
            "course",
            "teacher",
            "classroom",
            "date",
            "start_time",
            "end_time",
            "group_name",
        )

class AttendanceSerializer(serializers.ModelSerializer):
    lesson = LessonSerializer()

    class Meta:
        model = Attendance
        fields = ("lesson", "attended",)

class HomeworkSerializer(serializers.ModelSerializer):
    lesson = LessonSerializer()
    status_color = serializers.SerializerMethodField()  

    class Meta:
        model = Homework
        fields = ("lesson", "score", "status_color")  

    def get_status_color(self, obj):
        if obj.score >= 9:
            return "green"
        elif obj.score >= 6:
            return "orange"
        else:
            return "red"


class CurriculumSerializer(serializers.ModelSerializer):
    course = serializers.StringRelatedField()

    class Meta:
        model = Curriculum
        fields = ("course", "month_number", "title", "lessons_outline")

class StatisticsSerializer(serializers.Serializer):
    homework_avg = serializers.DecimalField(max_digits=5, decimal_places=2)
    attendance_percent = serializers.DecimalField(max_digits=5, decimal_places=2)


class DiscountPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountPolicy
        fields = "__all__"