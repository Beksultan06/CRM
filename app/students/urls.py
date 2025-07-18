from rest_framework.routers import DefaultRouter
from .views import (
    LessonViewSet,
    AttendanceViewSet,
    HomeworkViewSet,
    CurriculumViewSet,
    StatisticsViewSet,
)
from .views_extra import ReportTableView, DiscountPolicyView

router = DefaultRouter()
router.register(r"lessons", LessonViewSet, basename="student-lessons")
router.register(r"attendance", AttendanceViewSet, basename="student-attendance")
router.register(r"homework", HomeworkViewSet, basename="student-homework")
router.register(r"curriculum", CurriculumViewSet, basename="student-curriculum")
router.register(r"statistics", StatisticsViewSet, basename="student-statistics")

urlpatterns = [
    path("next-lesson/", NextLessonView.as_view(), name="next-lesson"),
    path("report-table/", ReportTableView.as_view(), name="report-table"),
    path("discount-policy/", DiscountPolicyView.as_view(), name="discount-policy"),
]


urlpatterns = router.urls