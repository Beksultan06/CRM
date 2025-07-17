from rest_framework.routers import DefaultRouter
from .views import StudentRequestViewSet, ManagerLessonViewSet, StudentViewSet, PaymentViewSet, PaymentReminderViewSet, UpcomingRemindersView, FinancialSummaryPDFView, TeacherReportPDFView
from django.urls import path

router = DefaultRouter()
router.register(r"requests", StudentRequestViewSet, basename="manager-requests")
router.register(r"lessons", ManagerLessonViewSet, basename="manager-lessons")
router.register(r"students", StudentViewSet, basename="manager-students")
router.register(r"payments", PaymentViewSet, basename="manager-payments")
router.register(r"reminders", PaymentReminderViewSet, basename="manager-reminders")

urlpatterns = [
    path("reminders/upcoming/", UpcomingRemindersView.as_view(), name="upcoming-reminders"),
    path("report/pdf/summary/", FinancialSummaryPDFView.as_view(), name="pdf-summary"),
    path("report/pdf/teachers/", TeacherReportPDFView.as_view(), name="pdf-teachers"),
]

urlpatterns = router.urls