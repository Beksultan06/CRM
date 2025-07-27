from rest_framework import serializers
from app.manager.models import Payment
from app.administator.models import Notification

class AdminPaymentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    payment_method = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            "id",
            "date",
            "student_name",
            "course_name",
            "amount_cash",
            "amount_transfer",
            "amount_online",
            "total_amount",
            "status",
            "comment",
            "payment_method",
        ]
        ref_name = "AdminPaymentSerializer"

    def get_payment_method(self, obj):
        if obj.amount_cash:
            return "Наличные"
        elif obj.amount_transfer:
            return "Перевод"
        elif obj.amount_online:
            return "Онлайн"
        return "Не указано"

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "message", "created_at", "is_read"]
        read_only_fields = ["id", "message", "created_at"]