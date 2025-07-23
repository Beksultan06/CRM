from rest_framework.routers import DefaultRouter
from app.administrator.views.dashboard import DashboardViewSet
from app.administrator.views.students import (
    NewStudentViewSet,
    StudentCountViewSet,
    StudentRequestCountViewSet,
)
from app.administrator.views.payments import PaymentSummaryViewSet
from app.administrator.views.attendance import AttendanceSummaryViewSet
from app.administrator.views.lessons import LessonTodayViewSet
from app.administrator.views.attendance import AttendanceSummaryViewSet

router = DefaultRouter()
router.register(r'dashboard', DashboardViewSet, basename='dashboard')
router.register(r'new-students', NewStudentViewSet, basename='new-students')
router.register(r'students-count', StudentCountViewSet, basename='students-count')
router.register(r'requests-count', StudentRequestCountViewSet, basename='requests-count')
router.register(r'payment-summary', PaymentSummaryViewSet, basename='payment-summary')
router.register(r'attendance-summary', AttendanceSummaryViewSet, basename='attendance-summary')
router.register(r'lessons-today', LessonTodayViewSet, basename='lessons-today')
router.register(r'attendance-summary', AttendanceSummaryViewSet, basename='attendance-summary')

urlpatterns = router.urls
