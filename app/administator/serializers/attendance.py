from rest_framework import serializers
from app.students.models import Attendance

class AttendanceSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    lesson_date = serializers.DateField(source='lesson.date', read_only=True)

    class Meta:
        model = Attendance
        fields = ['id', 'lesson_title', 'lesson_date', 'status']
