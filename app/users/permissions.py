from rest_framework.permissions import IsAuthenticated

class IsAdmin(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == 'Администратор'

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "Менеджер")

class IsStudent(BasePermission):
    """Разрешить доступ только аутентифицированным пользователям с ролью == 'Ученик'."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "Ученик")

class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "Преподаватель"