from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app.administator.models import Dialog, Message
from app.administator.serializers.chat import DialogSerializer, MessageSerializer

class DialogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DialogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):   
            return Dialog.objects.none()
        return Dialog.objects.filter(participants=self.request.user)

    @action(detail=True, methods=["get"])
    def messages(self, request, pk=None):
        dialog = self.get_object()
        messages = dialog.messages.order_by("created_at")
        return Response(MessageSerializer(messages, many=True).data)

    @action(detail=True, methods=["post"])
    def send(self, request, pk=None):
        dialog = self.get_object()
        message = Message.objects.create(
            dialog=dialog,
            sender=request.user,
            text=request.data.get("text", "")
        )
        return Response(MessageSerializer(message).data)
