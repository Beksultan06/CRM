from rest_framework import viewsets
from rest_framework.response import Response
from app.administator.services import lessons
from app.administator.permissions import IsAdminUserRole
from app.students.serializers import LessonSerializer
from app.students.models import Lesson
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters


class LessonTodayViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUserRole]

    def list(self, request):
        return Response(lessons.today_lessons())

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.select_related('teacher', 'group').all()
    serializer_class = LessonSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['date', 'room', 'group']