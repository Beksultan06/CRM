from rest_framework import viewsets
from rest_framework.response import Response
from administrator.services import attendance
from app.administrator.permissions import IsAdminUserRole


class AttendanceSummaryViewSet(viewsets.ViewSet):
    """
    Статистика посещаемости за сегодня:
    - общее количество занятий
    - всего учеников
    - сколько присутствовали
    - сколько отсутствовали
    - проценты
    """
    permission_classes = [IsAdminUserRole]

    def list(self, request):
        data = attendance.today_summary()
        return Response({"attendance": data})
