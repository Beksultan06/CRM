from rest_framework import viewsets
from rest_framework.response import Response
from app.administator.services import (
    attendance,
    lessons,
    payments,
    students,
)

class DashboardViewSet(viewsets.ViewSet):
    """ Главный дашборд администратора """

    def list(self, request):
        return Response({
            "new_students_today": students.new_students_today(),
            "student_count": students.total_students(),
            "requests": students.requests_stat(),
            "payments": payments.today_summary(),
            "attendance": attendance.today_summary(),
            "lessons_today": lessons.today_lessons()
        })
