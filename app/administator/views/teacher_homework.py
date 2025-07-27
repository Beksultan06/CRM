from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from app.administator.permissions import IsAdminUserRole
from app.teacher.models import HomeworkSubmission
from app.administator.serializers.teacher_homework import HomeworkReviewSerializer

class TeacherHomeworkViewSet(viewsets.ModelViewSet):
    serializer_class = HomeworkReviewSerializer
    permission_classes = [IsAdminUserRole]

    def get_queryset(self):
        return HomeworkSubmission.objects.filter(
            lesson__teacher=self.request.user
        ).select_related("student", "lesson").order_by("-submitted_at")

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save(
            reviewed=True,
            reviewed_at=timezone.now(),
            reviewed_by=request.user
        )
        return Response(serializer.data)