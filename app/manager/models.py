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

    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="Курс")
    message = models.TextField(blank=True, verbose_name="Сообщение")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new", verbose_name="Статус")
    assigned_to = models.ForeignKey(
        CustomUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={"role": "Менеджер"},
        verbose_name="Менеджер"
    )
    source = models.CharField(max_length=100, default="Форма на сайте", verbose_name="Источник")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    scheduled_at = models.DateTimeField(blank=True, null=True, verbose_name="Запланировано на")

    class Meta:
        verbose_name = "Заявка ученика"
        verbose_name_plural = "Заявки учеников"
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

    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="payments", verbose_name="Ученик")
    course = models.ForeignKey(Course, on_delete=models.PROTECT, verbose_name="Курс")
    amount_cash = models.PositiveIntegerField(default=0, verbose_name="Наличные")
    amount_transfer = models.PositiveIntegerField(default=0, verbose_name="Перевод")
    amount_online = models.PositiveIntegerField(default=0, verbose_name="Онлайн оплата")
    total_amount = models.PositiveIntegerField(verbose_name="Итоговая сумма")
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="paid", verbose_name="Статус")
    date = models.DateField(auto_now_add=True, verbose_name="Дата оплаты")

    class Meta:
        verbose_name = "Платёж"
        verbose_name_plural = "Платежи"
        ordering = ["-date"]

class PaymentReminder(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Ученик")
    course = models.ForeignKey(Course, on_delete=models.PROTECT, verbose_name="Курс")
    message = models.TextField(verbose_name="Сообщение")
    amount = models.PositiveIntegerField(verbose_name="Сумма")
    due_date = models.DateField(verbose_name="Срок оплаты")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Напоминание об оплате"
        verbose_name_plural = "Напоминания об оплате"

    def __str__(self):
        return f"Напоминание: {self.student.get_full_name()} - {self.course.name}"

class TeacherRate(models.Model):
    teacher = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "Преподаватель"},
        verbose_name="Преподаватель"
    )
    rate_per_lesson = models.PositiveIntegerField(verbose_name="Ставка за урок")

    class Meta:
        verbose_name = "Ставка преподавателя"
        verbose_name_plural = "Ставки преподавателей"

class TeacherBonus(models.Model):
    teacher = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "Преподаватель"},
        verbose_name="Преподаватель"
    )
    amount = models.PositiveIntegerField(verbose_name="Сумма бонуса")
    month = models.DateField(verbose_name="Месяц")

    class Meta:
        verbose_name = "Бонус преподавателя"
        verbose_name_plural = "Бонусы преподавателей"

class Expense(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    amount = models.PositiveIntegerField(verbose_name="Сумма")
    category = models.CharField(max_length=100, verbose_name="Категория")
    date = models.DateField(verbose_name="Дата")

    class Meta:
        verbose_name = "Расход"
        verbose_name_plural = "Расходы"

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Пользователь")
    message = models.TextField(verbose_name="Сообщение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_read = models.BooleanField(default=False, verbose_name="Прочитано")

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"
