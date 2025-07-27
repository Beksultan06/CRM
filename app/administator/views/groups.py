from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from app.teacher.models import Group
from app.administator.serializers.groups import AdminGroupSerializer
from app.administator.permissions import IsAdminUserRole

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all().select_related("teacher")
    serializer_class = AdminGroupSerializer
    permission_classes = [IsAdminUserRole]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["name", "teacher__first_name", "teacher__last_name"]
    filterset_fields = ["status", "format"]
