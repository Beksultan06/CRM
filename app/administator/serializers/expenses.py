from rest_framework import serializers
from app.manager.models import Expense

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ["id", "name", "amount", "category", "date"]
