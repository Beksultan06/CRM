from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models.functions import TruncMonth
from django.db.models import Sum
from app.manager.models import Payment
from app.administator.permissions import IsAdminUserRole

class PaymentReportView(APIView):
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        data = (
            Payment.objects
            .annotate(month=TruncMonth("date"))
            .values("month")
            .annotate(total=Sum("total_amount"))
            .order_by("month")
        )
        return Response(data)
