from rest_framework import viewsets
from rest_framework.response import Response
from administrator.services import lessons
from app.administrator.permissions import IsAdminUserRole

class LessonTodayViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUserRole]

    def list(self, request):
        return Response(lessons.today_lessons())
