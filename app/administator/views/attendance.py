from rest_framework import viewsets
from rest_framework.response import Response
from app.administator.services import attendance
from app.administator.permissions import IsAdminUserRole
from app.administator.serializers.attendance import AttendanceSerializer


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

class AttendanceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        student_id = self.kwargs['student_id']
        return Attendance.objects.filter(student_id=student_id).select_related('lesson')