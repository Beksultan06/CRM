from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="CRM",
        default_version='v1',
        description="CRM description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="nurlanuuulubeksultan@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/v1/users/", include("app.users.urls")),
    path("api/v1/administration/", include("app.administration.urls")),
    path("api/v1/manager/", include("app.manager.urls")),
    path("api/v1/teacher/", include("app.teacher.urls")),
    path("api/v1/student/", include("app.student.urls")),

    # Swagger и Redoc
    path('swagger<str:format>', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # React SPA
    path("", TemplateView.as_view(template_name="index.html")),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
