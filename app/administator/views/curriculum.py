from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from app.students.models import Curriculum
from app.administator.serializers.curriculum import CurriculumSerializer
from app.administator.permissions import IsAdminUserRole


class CurriculumViewSet(viewsets.ModelViewSet):
    queryset = Curriculum.objects.all().select_related("course")
    serializer_class = CurriculumSerializer
    permission_classes = [IsAuthenticated, IsAdminUserRole]

    def get_queryset(self):
        queryset = super().get_queryset()
        course_id = self.request.query_params.get("course")
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        return queryset
