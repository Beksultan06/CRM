from rest_framework import serializers
from app.users.models import CustomUser
from app.administator.models import TeacherSalary

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
