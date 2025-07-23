from rest_framework import viewsets
from rest_framework.response import Response
from administrator.services import payments
from app.administrator.permissions import IsAdminUserRole

class PaymentSummaryViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUserRole]

    def list(self, request):
        return Response({"payments": payments.today_summary()})
