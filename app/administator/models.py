from django.db import models
from app.users.models import CustomUser
# Create your models here.
class TeacherSalary(models.Model):
    SALARY_TYPE_CHOICES = [
        ("fixed", "Фиксированная ставка"),
        ("hourly", "Почасовая ставка"),
    ]

    teacher = models.OneToOneField(CustomUser, on_delete=models.CASCADE, limit_choices_to={"role": "Преподаватель"})
    salary_type = models.CharField(max_length=10, choices=SALARY_TYPE_CHOICES)
    amount = models.PositiveIntegerField()

    class Meta:
        verbose_name = "Зарплата преподавателя"
        verbose_name_plural = "Зарплаты преподавателей"
