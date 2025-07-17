from django.db import models
from app.users.models import CustomUser
from app.students.models import Course, Lesson

class StudentRequest(models.Model):
    STATUS_CHOICES = [
        ("new", "Новая"),
        ("in_progress", "В работе"),
        ("booked", "Записан"),
        ("rejected", "Отказ"),
    ]

    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    assigned_to = models.ForeignKey(
        CustomUser, null=True, blank=True, on_delete=models.SET_NULL, limit_choices_to={"role": "Менеджер"}
    )
    source = models.CharField(max_length=100, default="Форма на сайте")
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["assigned_to"]),
        ]
        ordering = ["-created_at"]

class Payment(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ("cash", "Наличные"),
        ("transfer", "Перевод"),
        ("online", "Онлайн"),
    ]
    STATUS_CHOICES = [
        ("pending", "Ожидается"),
        ("paid", "Оплачено"),
    ]

    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="payments")
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    amount_cash = models.PositiveIntegerField(default=0)
    amount_transfer = models.PositiveIntegerField(default=0)
    amount_online = models.PositiveIntegerField(default=0)
    total_amount = models.PositiveIntegerField()
    comment = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="paid")
    date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

class PaymentReminder(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    message = models.TextField()
    amount = models.PositiveIntegerField()
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Напоминание: {self.student.get_full_name()} - {self.course.name}"

class TeacherRate(models.Model):
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={"role": "Преподаватель"})
    rate_per_lesson = models.PositiveIntegerField()

class TeacherBonus(models.Model):
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={"role": "Преподаватель"})
    amount = models.PositiveIntegerField()
    month = models.DateField()

class Expense(models.Model):
    name = models.CharField(max_length=255)
    amount = models.PositiveIntegerField()
    category = models.CharField(max_length=100)
    date = models.DateField()

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
