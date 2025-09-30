from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("Имя пользователя обязательно")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE = (
        ("Administrator", "Администратор"),
        ("Manager", "Менеджер"),
        ("Teacher", "Преподаватель"),
        ("Student", "Ученик"),
    )

    username = models.CharField(max_length=150, unique=True, verbose_name="Имя пользователя")
    first_name = models.CharField(max_length=150, blank=True, verbose_name="Имя", null=True)
    last_name = models.CharField(max_length=150, blank=True, verbose_name="Фамилия", null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="ФИО")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    telegram = models.CharField(max_length=100, blank=True, verbose_name="Телеграм")
    role = models.CharField(max_length=20, choices=ROLE, default="Student", verbose_name="Роль")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_staff = models.BooleanField(default=True, verbose_name="Сотрудник")
    age = models.CharField(max_length=3, verbose_name="Возраст", null=True)
    date_joined = models.DateTimeField(default=timezone.now, verbose_name="Дата регистрации")
    avatarka = models.FileField(upload_to="avatarka/", verbose_name="Изображение Профиля Файл", blank=False, null=True)
    email = models.EmailField(unique=True, verbose_name="Email", blank=True, null=True)
    left_date = models.DateTimeField(null=True, blank=True, verbose_name="Дата ухода")


    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.role})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def save(self, *args, **kwargs):
        if not self.is_active and self.left_date is None:
            self.left_date = timezone.now()
        elif self.is_active:
            self.left_date = None
        super().save(*args, **kwargs)

