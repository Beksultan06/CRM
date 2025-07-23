from rest_framework import serializers
from app.manager.models import StudentRequest
from app.users.models import CustomUser
from app.students.models import Course

class ManagerMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "first_name", "last_name"]


class CourseMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id", "name"]

class StudentRequestSerializer(serializers.ModelSerializer):
    course = CourseMiniSerializer()
    assigned_to = ManagerMiniSerializer(allow_null=True)

    class Meta:
        model = StudentRequest
        fields = [
            "id", "full_name", "phone", "email",
            "status", "course", "assigned_to",
            "message", "source", "created_at", "scheduled_at"
        ]

class StudentRequestUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentRequest
        fields = ["status", "assigned_to", "scheduled_at"]

class StudentRequestShortSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)

    class Meta:
        model = StudentRequest
        fields = ['id', 'full_name', 'phone', 'course_name', 'status']