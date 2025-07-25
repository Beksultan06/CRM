from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from app.users.models import CustomUser
from app.administator.models import TeacherSalary
from app.administator.serializers.teachers import TeacherSerializer, TeacherSalarySerializer

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.filter(role="Преподаватель")
    serializer_class = TeacherSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ["first_name", "last_name", "username"]
    filterset_fields = ["group__course__name"]

    @action(detail=True, methods=["put"], url_path="salary")
    def update_salary(self, request, pk=None):
        teacher = self.get_object()
        salary, _ = TeacherSalary.objects.get_or_create(teacher=teacher)
        serializer = TeacherSalarySerializer(salary, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
