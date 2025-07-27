from rest_framework import serializers
from app.administator.models import GroupScheduleConfig

class GroupScheduleConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupScheduleConfig
        fields = [
            "planned_start",
            "lessons_per_month",
            "lessons_per_week",
            "lesson_duration",
            "is_manual",
        ]
