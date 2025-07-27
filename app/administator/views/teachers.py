from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response

from app.users.models import CustomUser
from app.teacher.models import Group
from app.users.models import CustomUser
from app.administator.models import TeacherSalary
from app.administator.serializers.teachers import TeacherSerializer, TeacherSalarySerializer, TeacherStudentSerializer, TeacherLessonSerializer, TeacherSalarySummarySerializer, TeacherCalendarLessonSerializer
from app.administator.permissions import IsAdminUserRole
from app.students.models import Enrollment
from app.students.models import Lesson

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.filter(role="Преподаватель")
    serializer_class = TeacherSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ["first_name", "last_name", "username"]
    filterset_fields = ["group__course__name"]
    permission_classes = [IsAdminUserRole]

    @action(detail=True, methods=["put"], url_path="salary")
    def update_salary(self, request, pk=None):
        teacher = self.get_object()
        salary, _ = TeacherSalary.objects.get_or_create(teacher=teacher)
        serializer = TeacherSalarySerializer(salary, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class TeacherStudentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TeacherStudentSerializer
    permission_classes = [IsAdminUserRole]

    def get_queryset(self):
        teacher_id = self.kwargs["teacher_id"]
        return Enrollment.objects.filter(group__teacher_id=teacher_id).select_related("student", "group", "course")

class TeacherLessonViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TeacherLessonSerializer
    permission_classes = [IsAdminUserRole]

    def get_queryset(self):
        teacher_id = self.kwargs["teacher_id"]
        return Lesson.objects.filter(teacher_id=teacher_id).select_related("course", "group", "classroom").order_by("-date")

class TeacherSalarySummaryViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUserRole]

    def list(self, request, teacher_id=None):
        serializer = TeacherSalarySummarySerializer(context={"teacher_id": teacher_id})
        return Response(serializer.data)


class TeacherCalendarView(APIView):
    permission_classes = [IsAdminUserRole]

    def get(self, request, teacher_id):
        lessons = Lesson.objects.filter(teacher_id=teacher_id).order_by("date", "start_time")
        serializer = TeacherCalendarLessonSerializer(lessons, many=True)
        return Response(serializer.data)