from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app.administator.services import attendance as attendance_service
from app.administator.permissions import IsAdminUserRole
from app.administator.serializers.attendance import (
    AttendanceSerializer,
    AttendanceStudentSerializer,
    BulkAttendanceUpdateSerializer,
    LessonSummarySerializer
)
from app.students.models import Lesson, Attendance


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
        if getattr(self, 'swagger_fake_view', False):
            return Response({})
        data = attendance_service.today_summary()
        return Response({"attendance": data})


class AttendanceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Attendance.objects.none()

        student_id = self.kwargs.get("student_id")
        if not student_id:
            return Attendance.objects.none()
        return Attendance.objects.filter(student_id=student_id).select_related("lesson")


class LessonAttendanceViewSet(viewsets.ViewSet):
    serializer_class = LessonSummarySerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        if getattr(self, 'swagger_fake_view', False):
            return Response([])

        lessons = Lesson.objects.filter(teacher=request.user).order_by("-date", "-start_time")
        data = [
            {
                "id": lesson.id,
                "date": lesson.date,
                "group": lesson.group_name,
                "course": lesson.course.name,
                "time": f"{lesson.start_time} - {lesson.end_time}"
            }
            for lesson in lessons
        ]
        return Response(data)

    @action(detail=True, methods=["get"])
    def students(self, request, pk=None):
        if getattr(self, 'swagger_fake_view', False):
            return Response([])

        lesson = Lesson.objects.filter(id=pk, teacher=request.user).first()
        if not lesson:
            return Response({"detail": "Занятие не найдено."}, status=status.HTTP_404_NOT_FOUND)

        attendance_qs = Attendance.objects.filter(lesson=lesson).select_related("student")
        serializer = AttendanceStudentSerializer(attendance_qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["put"])
    def update_attendance(self, request, pk=None):
        if getattr(self, 'swagger_fake_view', False):
            return Response({"detail": "Swagger view"}, status=status.HTTP_200_OK)

        serializer = BulkAttendanceUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(
            {"detail": f"{result['updated']} записей обновлено."},
            status=status.HTTP_200_OK
        )
