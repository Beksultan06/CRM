# teacher/urls.py
from rest_framework.routers import DefaultRouter
from .views import (
    HomeworkSubmissionViewSet,
    GroupDetailView,
    GroupListView,
    GroupStudentsView,
    GroupHomeworkView,
    GroupAttendanceView,
    GroupStatisticsView,
    GroupCurriculumView,
)
from django.urls import path

router = DefaultRouter()
router.register("homeworks", HomeworkSubmissionViewSet)

urlpatterns = [
    path("groups/", GroupListView.as_view()),
    path("group/<int:pk>/", GroupDetailView.as_view()),
    path("group/<int:pk>/students/", GroupStudentsView.as_view()),
    path("group/<int:pk>/homeworks/", GroupHomeworkView.as_view()),
    path("group/<int:pk>/attendances/", GroupAttendanceView.as_view()),
    path("group/<int:pk>/statistics/", GroupStatisticsView.as_view()),
    path("group/<int:pk>/curriculum/", GroupCurriculumView.as_view()),
]

urlpatterns += router.urls 
