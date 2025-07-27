from rest_framework import viewsets
from rest_framework.response import Response
from app.administator.services import payments
from app.administator.permissions import IsAdminUserRole
from app.manager.models import Payment
from app.administator.serializers.payments import AdminPaymentSerializer
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

class PaymentSummaryViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUserRole]

    def list(self, request):
        return Response({"payments": payments.today_summary()})

class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Payment.objects.select_related("student", "course").all()
    serializer_class = AdminPaymentSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["student", "course", "status", "date"]
    search_fields = ["student__first_name", "student__last_name", "course__name"]