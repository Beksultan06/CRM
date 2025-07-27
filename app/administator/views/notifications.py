from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from app.administator.models import Notification
from app.administator.serializers.notifications import NotificationSerializer, NotificationSerializers
from app.administator.permissions import IsAdminUserRole

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAdminUserRole]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Notification.objects.none()

        return Notification.objects.filter(user=self.request.user).order_by("-created_at")

class NotificationViewSets(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializers
    permission_classes = [IsAdminUserRole]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by("-created_at")

    @action(detail=True, methods=["post"], url_path="mark-as-read")
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({"status": "marked as read"})