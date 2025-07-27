from rest_framework.routers import DefaultRouter
from django.urls import path
from app.administator.views.dashboard import DashboardViewSet
from app.administator.views.students import (
    NewStudentViewSet,
    StudentCountViewSet,
    StudentRequestCountViewSet,
    StudentViewSet,
)
from app.administator.views.payments import (
    PaymentSummaryViewSet,
    PaymentViewSet,
)
from app.administator.views.attendance import (
    AttendanceSummaryViewSet,
    AttendanceViewSet,
)
from app.administator.views.lessons import (
    LessonTodayViewSet,
    LessonViewSet,
)
from app.administator.views.requests import StudentRequestViewSet, StudentFilterRequestViewSet
from app.administator.views.teachers import TeacherViewSet, TeacherStudentViewSet, TeacherLessonViewSet
from app.administator.views.teacher_homework import TeacherHomeworkViewSet as Teascher
from app.administator.views.attendance import LessonAttendanceViewSet
from app.administator.views.schedule import TeacherScheduleViewSet
from app.administator.views.notifications import NotificationViewSet, NotificationViewSets
from app.administator.views.chat import DialogViewSet
from app.administator.views.homeworks import TeacherHomeworkViewSet as HomeWorks
from app.administator.views.curriculum import CurriculumViewSet
from app.administator.views.group_schedule import GroupScheduleViewSet
from app.administator.views.groups import GroupViewSet
from app.administator.views.teachers import TeacherCalendarView
from app.administator.views.expenses import ExpenseViewSet
from app.administator.views.reports import PaymentReportView

router = DefaultRouter()

router.register(r'dashboard', DashboardViewSet, basename='dashboard')
router.register(r'new-students', NewStudentViewSet, basename='new-students')
router.register(r'students-count', StudentCountViewSet, basename='students-count')
router.register(r'requests-count', StudentRequestCountViewSet, basename='requests-count')
router.register(r'payment-summary', PaymentSummaryViewSet, basename='payment-summary')
router.register(r'attendance-summary', AttendanceSummaryViewSet, basename='attendance-summary')
router.register(r'lessons-today', LessonTodayViewSet, basename='lessons-today')
router.register(r'students', StudentViewSet, basename='students')
router.register(r'payments', PaymentViewSet, basename='payments')
router.register(r'attendances', AttendanceViewSet, basename='attendances')
router.register(r'lessons', LessonViewSet, basename='lessons')
router.register(r'requests', StudentRequestViewSet, basename='student-requests')
router.register(r'requests-filters', StudentFilterRequestViewSet, basename='student-requests-filters')
router.register(r'teachers', TeacherViewSet, basename='teachers')
router.register(r'teachers/(?P<teacher_id>\d+)/students', TeacherStudentViewSet, basename='teacher-students')
router.register(
    r'teachers/(?P<teacher_id>\d+)/lessons',
    TeacherLessonViewSet,
    basename='teacher-lessons'
)
router.register(r'lesson-attendance', LessonAttendanceViewSet, basename='lesson-attendance')
router.register(r'schedule', TeacherScheduleViewSet, basename='teacher-schedule')
router.register(r'notification', NotificationViewSet, basename='teacher-notifications')
router.register(r'chat', DialogViewSet, basename='chat')
router.register(r'curriculum', CurriculumViewSet, basename='curriculum')
router.register(r'groups', GroupScheduleViewSet, basename='group-schedule')
router.register(r'groups', GroupViewSet, basename='groups')
router.register(r'notifications', NotificationViewSets, basename='notifications')
router.register(r'expenses', ExpenseViewSet, basename='expenses')
router.register(r'homeworks_teachers', Teascher, basename='teacher-homeworks-teachers')
router.register(r'homeworks', HomeWorks, basename='teacher-homeworks')  # оставить

urlpatterns = router.urls

urlpatterns += [
    path("teachers/<int:teacher_id>/calendar/", TeacherCalendarView.as_view(), name="teacher-calendar"),
    path("reports/payments/", PaymentReportView.as_view(), name="payment-report"),
]