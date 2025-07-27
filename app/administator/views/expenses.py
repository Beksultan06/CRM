from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from app.manager.models import Expense
from app.administator.serializers.expenses import ExpenseSerializer
from app.administator.permissions import IsAdminUserRole

class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all().order_by("-date")
    serializer_class = ExpenseSerializer
    permission_classes = [IsAdminUserRole]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ["category", "date"]
    search_fields = ["name"]
