from rest_framework import serializers
from app.teacher.models import Group

class AdminGroupSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source="teacher.get_full_name", read_only=True)

    class Meta:
        model = Group
        fields = [
            "id",
            "name",
            "teacher",
            "teacher_name",
            "status",
            "format",
            "age_group",
            "created_at",
        ]
        read_only_fields = ["created_at"]
        ref_name = "AdminGroupSerializer"