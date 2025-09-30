from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app.administration.views import (
    GroupViewSet, PaymentViewSet, 
    GroupDashboardView, StudentTableViewSet,
    ExpenseViewSet, TeacherPaymentViewSet, 
    FinancialReportViewSet, 
    ClassroomViewSet, ScheduleViewSet, DailyScheduleView,
    ActiveStudentsAnalytics, TeacherWorkloadAnalytics, PopularCoursesAnalytics,
    StudentAttendanceView, StudentPaymentsView, LeadViewSet, AdminDashboardView
    )

router = DefaultRouter()
router.register(r'groups', GroupViewSet, basename='group')
router.register(r'student-table', StudentTableViewSet, basename='student-table')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'financial-reports', FinancialReportViewSet, basename='financial-report')
router.register(r'expenses', ExpenseViewSet, basename='expense')
router.register(r'teacher-payments', TeacherPaymentViewSet, basename='teacher-payment')
router.register(r'classrooms', ClassroomViewSet, basename='classroom')
router.register(r'schedule', ScheduleViewSet, basename='schedule')
router.register(r'leads', LeadViewSet, basename='lead')

urlpatterns = [
    path('', include(router.urls)),
    path('groups/<int:id>/dashboard/', GroupDashboardView.as_view(), name='group-dashboard'),
    path('daily-schedule/', DailyScheduleView.as_view(), name='daily-schedule'),
    path('active-students/', ActiveStudentsAnalytics.as_view(), name='active-students'),
    path('teacher-workload/', TeacherWorkloadAnalytics.as_view(), name='teacher-workload'),
    path('popular-courses/', PopularCoursesAnalytics.as_view(), name='popular-courses'),
    path('students/<int:student_id>/attendance/', StudentAttendanceView.as_view(), name='student-attendance'),
    path('students/<int:student_id>/payments/', StudentPaymentsView.as_view(), name='student-payments'),
    path('admin-dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
]