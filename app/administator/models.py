from django.db import models
from app.users.models import CustomUser
from app.teacher.models import Group
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

class GroupScheduleConfig(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name="schedule_config", verbose_name="Группа")
    planned_start = models.DateField(verbose_name="Планируемое начало")
    lessons_per_month = models.PositiveSmallIntegerField(verbose_name="Занятий в месяц")
    lessons_per_week = models.CharField(max_length=100, verbose_name="Занятий в неделю (напр. 'Пн/Ср')")
    lesson_duration = models.DurationField(verbose_name="Длительность занятия (напр. 2 часа)")
    is_manual = models.BooleanField(default=False, verbose_name="Распределение вручную")

    class Meta:
        verbose_name = "Настройка расписания группы"
        verbose_name_plural = "Настройки расписания групп"

class TeacherBonus(models.Model):
    teacher = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "Преподаватель"},
        verbose_name="Преподаватель",
        related_name="admin_teacher_bonuses"  # ← добавь
    )
    amount = models.PositiveIntegerField(verbose_name="Сумма бонуса")
    month = models.DateField(verbose_name="Месяц") 

    class Meta:
        verbose_name = "Бонус преподавателя"
        verbose_name_plural = "Бонусы преподавателей"
        unique_together = ("teacher", "month")

    def __str__(self):
        return f"{self.teacher.get_full_name()} — {self.month.strftime('%B %Y')}: {self.amount} сом"

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="admin_notifications")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

class Dialog(models.Model):
    participants = models.ManyToManyField(CustomUser, related_name="dialogs")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Диалог {self.pk}"

class Message(models.Model):
    dialog = models.ForeignKey(Dialog, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Сообщение от {self.sender.username} ({self.created_at})"