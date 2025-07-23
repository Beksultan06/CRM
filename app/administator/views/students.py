from rest_framework import viewsets
from rest_framework.response import Response
from administrator.services import students
from app.administrator.permissions import IsAdminUserRole

class NewStudentViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUserRole]

    def list(self, request):
        return Response({"new_students_today": students.new_students_today()})


class StudentCountViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUserRole]

    def list(self, request):
        return Response({"student_count": students.total_students()})


class StudentRequestCountViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUserRole]

    def list(self, request):
        return Response({"requests": students.requests_stat()})
