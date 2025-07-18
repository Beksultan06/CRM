from rest_framework import generics, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg
from django.utils import timezone
from .models import Group, HomeworkSubmission
from app.students.models import Attendance, Homework, Curriculum, Lesson
from app.users.models import CustomUser
from .serializers import *

class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "Преподаватель"

class GroupListView(generics.ListAPIView):
    permission_classes = [IsTeacher]
    serializer_class = GroupSerializer

    def get_queryset(self):
        return Group.objects.filter(teacher=self.request.user)

class GroupDetailView(generics.RetrieveAPIView):
    permission_classes = [IsTeacher]
    serializer_class = GroupSerializer
    queryset = Group.objects.all()

class GroupStudentsView(generics.ListAPIView):
    permission_classes = [IsTeacher]
    serializer_class = GroupStudentSerializer

    def get_queryset(self):
        group_id = self.kwargs['pk']
        return CustomUser.objects.filter(enrollments__course__lessons__group_name=Group.objects.get(id=group_id).name, role="Ученик").distinct()

class GroupCurriculumView(generics.ListAPIView):
    permission_classes = [IsTeacher]
    serializer_class = GroupCurriculumSerializer

    def get_queryset(self):
        group_id = self.kwargs["pk"]
        return Curriculum.objects.filter(course__lessons__group_name=Group.objects.get(id=group_id).name).distinct()

class HomeworkSubmissionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsTeacher]
    queryset = HomeworkSubmission.objects.select_related("student", "lesson")
    serializer_class = HomeworkSubmissionSerializer

    @action(detail=True, methods=["post"], permission_classes=[IsTeacher])
    def review(self, request, pk=None):
        submission = self.get_object()
        serializer = HomeworkReviewSerializer(
            submission,
            data=request.data,
            context={'request': request},
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

class GroupAttendanceView(generics.ListAPIView):
    permission_classes = [IsTeacher]
    serializer_class = GroupAttendanceSerializer

    def get_queryset(self):
        group_id = self.kwargs["pk"]
        return Attendance.objects.filter(lesson__group_name=Group.objects.get(id=group_id).name)

class GroupStatisticsView(generics.RetrieveAPIView):
    permission_classes = [IsTeacher]
    serializer_class = GroupStatisticSerializer

    def get_object(self):
        group_id = self.kwargs["pk"]
        group_name = Group.objects.get(id=group_id).name
        attendance = Attendance.objects.filter(lesson__group_name=group_name)
        homework = Homework.objects.filter(lesson__group_name=group_name)
        return {
            "attendance_rate": attendance.aggregate(rate=Avg("attended"))['rate'] or 0.0,
            "avg_homework_score": homework.aggregate(avg=Avg("score"))['avg'] or 0.0
        }