from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import Lesson, Attendance, Homework, Curriculum, Enrollment
from .serializers import (
    LessonSerializer,
    AttendanceSerializer,
    HomeworkSerializer,
    CurriculumSerializer,
    StatisticsSerializer,
)
from .permissions import IsStudent

class LessonViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Возвращает расписание для текущего студента, отфильтрованное по диапазону дат."""
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsStudent]

    def get_queryset(self):
        student = self.request.user
        # Уроки, на которые ученик зачислен через курс ИЛИ имя группы соответствует зачислению
        return (
            Lesson.objects.filter(course__enrollments__student=student)
            .select_related("course", "teacher", "classroom")
            .order_by("date", "start_time")
        )

    #ДОПОЛНИТЕЛЬНО: filter ?date=YYYY‑MM‑DD
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        date_str = request.query_params.get("date")
        if date_str:
            try:
                date_obj = timezone.datetime.fromisoformat(date_str).date()
            except ValueError:
                return Response({"detail": "Invalid date"}, status=status.HTTP_400_BAD_REQUEST)
            queryset = queryset.filter(date=date_obj)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class AttendanceViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated, IsStudent]

    def get_queryset(self):
        return (
            Attendance.objects.for_student(self.request.user)
            .select_related("lesson__course", "lesson__teacher", "lesson__classroom")
            .order_by("lesson__date")
        )

class HomeworkViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = HomeworkSerializer
    permission_classes = [IsAuthenticated, IsStudent]

    def get_queryset(self):
        return (
            Homework.objects.for_student(self.request.user)
            .select_related("lesson__course", "lesson__teacher", "lesson__classroom")
            .order_by("lesson__date")
        )

class CurriculumViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = CurriculumSerializer
    permission_classes = [IsAuthenticated, IsStudent]
    queryset = Curriculum.objects.select_related("course").order_by("month_number")

class StatisticsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsStudent]

    @action(detail=False, methods=["get"], url_path="monthly")
    def monthly(self, request):
        """Return statistics for given month (?year=&month=) or current."""
        student = request.user
        today = timezone.localdate()
        year = int(request.query_params.get("year", today.year))
        month = int(request.query_params.get("month", today.month))

        attendance_qs = Attendance.objects.for_student(student).month(year, month)
        homework_qs = Homework.objects.for_student(student).month(year, month)
        att_stats = attendance_qs.attendance_rate()
        hw_stats = homework_qs.average_score()

        data = {
            "attendance_percent": round((att_stats["attended"] / att_stats["total"] * 100) if att_stats["total"] else 0, 2),
            "homework_avg": round(hw_stats["avg"] or 0, 2),
        }
        serializer = StatisticsSerializer(data)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="overall")
    def overall(self, request):
        """Overall statistics for the whole study period."""
        student = request.user
        att_stats = Attendance.objects.for_student(student).attendance_rate()
        hw_stats = Homework.objects.for_student(student).average_score()
        data = {
            "attendance_percent": round((att_stats["attended"] / att_stats["total"] * 100) if att_stats["total"] else 0, 2),
            "homework_avg": round(hw_stats["avg"] or 0, 2),
        }
        return Response(StatisticsSerializer(data).data)