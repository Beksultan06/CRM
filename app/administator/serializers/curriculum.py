from rest_framework import serializers
from app.students.models import Curriculum

class CurriculumSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)

    class Meta:
        model = Curriculum
        fields = [
            "id",
            "course",
            "course_name",
            "month_number",
            "title",
            "lessons_outline",
            "created_at",
        ]
        read_only_fields = ["created_at"]
