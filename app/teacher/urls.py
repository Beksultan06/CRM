from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app.administration.views import (
    GroupViewSet, TeacherViewSet, StudentViewSet, 
    LessonViewSet, AttendanceViewSet, PaymentViewSet, 
    GroupDashboardView, MonthsViewSet, GroupTableViewSet, StudentTableViewSet,
    ScheduleViewSet, DailyScheduleView, TeacherHomeworkViewSet,
    StudentAttendanceView,
    )

router = DefaultRouter()


router.register(r'lessons', LessonViewSet, basename='lesson')
router.register(r'attendances', AttendanceViewSet, basename='attendance')
router.register(r'student-table', StudentTableViewSet, basename='student-table')
router.register(r'schedule', ScheduleViewSet, basename='schedule')
router.register(r'group-table', GroupTableViewSet, basename='group_table')


urlpatterns = [
    path('', include(router.urls)),
    path('groups/<int:id>/dashboard/', GroupDashboardView.as_view(), name='group-dashboard'),
    path('daily-schedule/', DailyScheduleView.as_view(), name='daily-schedule'),
    path('students/<int:student_id>/attendance/', StudentAttendanceView.as_view(), name='student-attendance'),
    path("teacher/homework/", TeacherHomeworkViewSet.as_view({"get": "list", "patch": "partial_update", "put": "update"}), name='teacher-homework'),
    path("teacher/homework/<int:pk>/", TeacherHomeworkViewSet.as_view({"get": "retrieve", "patch": "partial_update", "put": "update"}), name='teacher-homework-checking'),
]