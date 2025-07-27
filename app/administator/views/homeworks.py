from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app.teacher.models import HomeworkSubmission
from app.administator.serializers.homeworks import (
    TeacherHomeworkSerializer,
    TeacherHomeworkCheckSerializer
)

class TeacherHomeworkViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TeacherHomeworkSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return HomeworkSubmission.objects.filter(
            lesson__teacher=self.request.user
        ).select_related("lesson", "student")

    @action(detail=True, methods=["put"], url_path="check")
    def check(self, request, pk=None):
        homework = self.get_object()
        serializer = TeacherHomeworkCheckSerializer(homework, data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Проверено"}, status=200)
