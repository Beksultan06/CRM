from rest_framework.routers import DefaultRouter
from .views import (
    LessonViewSet,
    AttendanceViewSet,
    HomeworkViewSet,
    CurriculumViewSet,
    StatisticsViewSet,
)

router = DefaultRouter()
router.register(r"lessons", LessonViewSet, basename="student-lessons")
router.register(r"attendance", AttendanceViewSet, basename="student-attendance")
router.register(r"homework", HomeworkViewSet, basename="student-homework")
router.register(r"curriculum", CurriculumViewSet, basename="student-curriculum")
router.register(r"statistics", StatisticsViewSet, basename="student-statistics")

urlpatterns = router.urls