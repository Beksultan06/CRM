from rest_framework.routers import DefaultRouter
from .views import AuthViewSet, CustomTokenObtainPairView, TokenRefreshView
from django.urls import path

router = DefaultRouter()
router.register(r"auth", AuthViewSet, basename="auth")

urlpatterns = [
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

urlpatterns = router.urls

