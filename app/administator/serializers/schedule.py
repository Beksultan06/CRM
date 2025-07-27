from rest_framework import serializers
from app.students.models import Lesson

class LessonScheduleSerializer(serializers.ModelSerializer):
    course = serializers.CharField(source="course.name")
    group = serializers.CharField(source="group.name", allow_null=True)
    classroom = serializers.CharField(source="classroom.label")

    class Meta:
        model = Lesson
        fields = ["id", "date", "start_time", "end_time", "course", "group", "classroom"]
