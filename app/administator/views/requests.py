from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils.dateparse import parse_date
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from app.manager.models import StudentRequest
from app.administator.serializers.requests import (
    StudentRequestSerializer,
    StudentRequestUpdateSerializer
)


class StudentRequestViewSet(viewsets.ModelViewSet):
    """
    API для работы с заявками:
    - фильтрация по статусу и дате
    - просмотр заявки
    - обновление статуса / назначение менеджера
    """
    queryset = StudentRequest.objects.select_related("assigned_to", "course").all()
    serializer_class = StudentRequestSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status", "assigned_to"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action in ["partial_update", "update"]:
            return StudentRequestUpdateSerializer
        return StudentRequestSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        date_str = self.request.query_params.get("date")
        if date_str:
            date_obj = parse_date(date_str)
            if date_obj:
                queryset = queryset.filter(created_at__date=date_obj)
        return queryset


class StudentFilterRequestViewSet(viewsets.ModelViewSet):
    serializer_class = StudentRequestSerializer
    queryset = StudentRequest.objects.select_related('course').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'created_at']
    search_fields = ['full_name', 'phone']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return StudentRequest.objects.none()
        teacher_id = self.kwargs["teacher_id"]
        return StudentRequest.objects.filter(course__teacher_id=teacher_id)
