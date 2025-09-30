from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app.administration.views import GroupViewSet, GroupDashboardView, ScheduleViewSet, StudentProgressView, MonthsViewSet, DiscountRegulationViewSet, StudentHomeworkViewSet


router = DefaultRouter()
router.register(r'schedule', ScheduleViewSet, basename='schedule')
router.register(r'groups', GroupViewSet, basename='group')
router.register(r'months', MonthsViewSet, basename='month')
router.register(r'discount-regulations', DiscountRegulationViewSet, basename='discountregulation')
router.register(r'homework', StudentHomeworkViewSet, basename='student-homework')

urlpatterns = [
    path('', include(router.urls)),
    path('groups/<int:id>/dashboard/', GroupDashboardView.as_view(), name='group-dashboard'),
    path('progress/', StudentProgressView.as_view(), name='progress-list'),
]