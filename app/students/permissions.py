from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsStudent(BasePermission):
    """Разрешить доступ только аутентифицированным пользователям с ролью == 'Ученик'."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "Ученик")