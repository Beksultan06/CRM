from rest_framework.routers import DefaultRouter

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
from app.administator.views.requests import StudentRequestViewSet

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

urlpatterns = router.urls
