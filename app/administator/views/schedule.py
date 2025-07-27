from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.timezone import now, timedelta
from app.students.models import Lesson
from app.administator.serializers.schedule import LessonScheduleSerializer

class TeacherScheduleViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        Уроки преподавателя на текущую неделю
        """
        today = now().date()
        end_of_week = today + timedelta(days=7)

        lessons = Lesson.objects.filter(
            teacher=request.user,
            date__range=[today, end_of_week]
        ).order_by("date", "start_time")

        serializer = LessonScheduleSerializer(lessons, many=True)
        return Response(serializer.data)
