from rest_framework import serializers
from app.manager.models import StudentRequest

class StudentProfileSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source="teacher.full_name", read_only=True)

    class Meta:
        model = StudentRequest
        fields = ['id', 'first_name', 'last_name', 'telegram', 'phone', 'login', 'direction', 'teacher_name']