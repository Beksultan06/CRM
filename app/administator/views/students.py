from rest_framework import viewsets
from rest_framework.response import Response
from app.administator.services import students
from app.administator.permissions import IsAdminUserRole
from app.administator.serializers.students import StudentProfileSerializer
from app.manager.models import StudentRequest
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

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

class StudentViewSet(viewsets.ModelViewSet):
    queryset = StudentRequest.objects.select_related('teacher').all()
    serializer_class = StudentProfileSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['direction']
    search_fields = ['first_name', 'last_name']