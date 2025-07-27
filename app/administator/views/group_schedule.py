from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from app.teacher.models import Group
from app.administator.models import GroupScheduleConfig
from app.administator.serializers.group_schedule import GroupScheduleConfigSerializer
from app.administator.permissions import IsAdminUserRole

class GroupScheduleViewSet(viewsets.GenericViewSet):
    queryset = GroupScheduleConfig.objects.select_related("group")
    serializer_class = GroupScheduleConfigSerializer
    permission_classes = [IsAdminUserRole]

    @action(detail=True, methods=["get", "put"], url_path="schedule")
    def schedule(self, request, pk=None):
        group = Group.objects.filter(pk=pk).first()
        if not group:
            return Response({"detail": "Группа не найдена."}, status=status.HTTP_404_NOT_FOUND)

        schedule, _ = GroupScheduleConfig.objects.get_or_create(group=group)

        if request.method == "GET":
            serializer = self.get_serializer(schedule)
            return Response(serializer.data)

        serializer = self.get_serializer(schedule, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
