from django.db import models
from django.forms import ValidationError
from app.users.models import CustomUser
from django.utils import timezone
from django.db.models import Sum
from django.db.models import Sum, F, ExpressionWrapper, DecimalField


class Direction(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название направления")

    class Meta:
        verbose_name = "Направление"
        verbose_name_plural = "Направления"

    def __str__(self):
        return self.name

class Group(models.Model):
    CREATION_TYPES = [
        ('auto', 'Автоматически'),
        ('manual', 'Вручную'),
    ]
    FORMAT_CHOICES = [
        ('online', 'Онлайн'),
        ('offline', 'Оффлайн'),
    ]
    group_name = models.CharField(max_length=255, verbose_name="Название группы")
    direction = models.ForeignKey(
        Direction,
        on_delete=models.PROTECT,
        related_name='groups',
        verbose_name="Направление"
    )
    age_group = models.CharField(max_length=50, verbose_name="Возрастная группа")
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, verbose_name="Формат")
    duration_months = models.PositiveIntegerField(verbose_name="Продолжительность (месяцы)")
    creation_date  = models.DateField(auto_now_add=True, verbose_name="Дата создания")
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    
    planned_start = models.DateField(verbose_name="Планируемое начало")
    lessons_per_month = models.PositiveIntegerField(verbose_name="Занятий в месяц")
    lesson_duration = models.PositiveIntegerField(verbose_name="Продолжительность занятия (часы)")
    lessons_per_week = models.PositiveIntegerField(verbose_name="Занятий в неделю")
    schedule_days = models.CharField(max_length=100, verbose_name="Дни занятий")
    is_active = models.BooleanField(default=True, verbose_name="Активный")
    
    teacher = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        limit_choices_to={'role': 'Teacher'},
        verbose_name="Преподаватель"
    )
    students = models.ManyToManyField(
        CustomUser,
        blank=True,
        related_name='student_groups',
        limit_choices_to={'role': 'Student'},
        verbose_name="Ученики"
    )

    creation_type = models.CharField(
        max_length=10,
        choices=CREATION_TYPES,
        default='manual',
        verbose_name="Режим создания"
    )
    homework_files = models.FileField(
        upload_to="homework",
        blank=True, null=True
    )

    @property
    def current_course(self):
        """Возвращает номер текущего курса группы"""
        if not self.creation_date:
            return 1
            
        today = timezone.now().date()
        months_passed = (today.year - self.creation_date.year) * 12 + (today.month - self.creation_date.month)
        current_course = (months_passed // self.duration_months) + 1
        return current_course
    
    @property
    def current_month(self):
        """Возвращает номер текущего месяца в курсе"""
        if not self.creation_date:
            return 1
            
        today = timezone.now().date()
        months_passed = (today.year - self.creation_date.year) * 12 + (today.month - self.creation_date.month)
        current_month = (months_passed % self.duration_months) + 1
        return current_month

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self):
        return f"{self.group_name} ({self.direction.name})"
    

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)


        if is_new and self.creation_type == 'auto':
            for month_num in range(1, self.duration_months + 1):
                month, _ = Months.objects.get_or_create(
                    group=self,
                    month_number=month_num,
                    defaults={
                        "title": f"Месяц {month_num}",
                        "description": f"Описание месяца {month_num}"
                    }
                )
                for lesson_num in range(1, self.lessons_per_month + 1):
                    lesson, _ = Lesson.objects.get_or_create(
                        month=month,
                        order=lesson_num,
                        defaults={
                            "title": f"Урок {lesson_num}",
                            "description": f"Описание урока {lesson_num}"
                        }
                    )
                    for student in self.students.all():
                        Attendance.objects.get_or_create(
                            lesson=lesson,
                            student=student,
                            defaults={"status": "0"}
                        )
                        HomeworkSubmission.objects.get_or_create(
                            lesson=lesson,
                            student=student,
                            defaults={"status": "black"}
                        )


class Teacher(models.Model):
    PAYMENT_TYPES = [
        ('fixed', 'Фиксированная ставка'),
        ('hourly', 'Почасовая ставка'),
    ]
    
    PERIOD_TYPES = [
        ('month', 'В месяц'),
        ('per_lesson', 'За занятие'),
    ]
    
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='teacher_add',
        verbose_name="Пользователь"
    )
    payment_type = models.CharField(
        max_length=10, 
        choices=PAYMENT_TYPES, 
        default='fixed',
        verbose_name="Тип оплаты"
    )
    payment_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Сумма оплаты"
    )
    payment_period = models.CharField(
        max_length=10, 
        choices=PERIOD_TYPES, 
        blank=True,
        verbose_name="Период оплаты"
    )
    
    # Связи с группами и направлениями
    groups = models.ManyToManyField(
        'Group',
        blank=True,
        related_name='teachers',
        verbose_name="Группы"
    )
    directions = models.ManyToManyField(
        Direction,
        blank=True,
        related_name='teachers',
        verbose_name="Направления"
    )
    
    class Meta:
        verbose_name = "Преподаватель"
        verbose_name_plural = "Преподаватели"

    def __str__(self):
        return f"{self.user.get_full_name()}"



class Student(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='student_add',
        verbose_name="Пользователь"
    )
    full_name = models.CharField(
        max_length=155,
        verbose_name='ФИО',
        default="Unknown",
        null=True, blank=True
    )
    # Связи с группами и направлениями
    groups = models.ManyToManyField(
        'Group',
        blank=True,
        related_name='student',
        verbose_name="Группы"
    )
    directions = models.ManyToManyField(
        Direction,
        blank=True,
        related_name='student',
        verbose_name="Направления"
    )
    
    class Meta:
        verbose_name = "Ученик"
        verbose_name_plural = "Ученики"

    def __str__(self):
        return f"{self.user.get_full_name()}"
    

class Months(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='months')
    month_number = models.PositiveIntegerField(verbose_name="Номер месяца")
    title = models.CharField(max_length=255, verbose_name="Название месяца")
    description = models.TextField(verbose_name="Описание месяца")
    
    class Meta:
        verbose_name = "Месяц курса"
        verbose_name_plural = "Месяцы курсов"
        ordering = ['month_number']
        unique_together = ('group', 'month_number')

    def __str__(self):
        return f"{self.group} - Месяц {self.month_number}"

class Lesson(models.Model):
    month = models.ForeignKey(Months, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255, verbose_name="Название урока")
    description = models.TextField(verbose_name="Описание урока")
    order = models.PositiveIntegerField(verbose_name="Порядковый номер")
    date = models.DateTimeField(verbose_name="Дата", null=True, blank=True)
    lesson_links = models.URLField(blank=True, verbose_name="Ссылки урока")
    homework_links = models.URLField(blank=True, verbose_name="Ссылки ДЗ")
    lesson_recording = models.URLField(
        blank=True,
        null=True,
        verbose_name="Запись урока"
    )
    homework_files = models.FileField(
        upload_to='homework_files/',
        blank=True,
        null=True,
        verbose_name="Файлы ДЗ"
    )
    homework_deadline = models.DateTimeField(null=True, blank=True, verbose_name='Срок выполнения')
    homework_description = models.TextField(blank=True, verbose_name='Описание задания')
    homework_requirements = models.TextField(blank=True, verbose_name='Требования к заданию')

    
    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ['order']
        unique_together = ('month', 'order')

    def __str__(self):
        return f"{self.month} - Урок {self.order}"
    


class HomeworkSubmission(models.Model):
    STATUS_CHOICES = [
        ('green', 'Правильно'),
        ('orange', 'Отправлено'),
        ('red', 'Отказано'),
        ('black', 'Не сделано'),
    ]
    
    lesson = models.ForeignKey(
        'Lesson',
        on_delete=models.CASCADE,
        related_name='homework_submissions',
        null=True, blank=True
    )
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='homework_submissions',
        verbose_name="Ученик",
        null=True, blank=True
    )
    
    # Ссылки на проект — JSONField, максимум 5 ссылок
    project_links = models.JSONField(
        verbose_name="Ссылки на проект",
        default=list,
        blank=True, null=True
    )


    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата отправки")
    status = models.CharField(
        verbose_name="Статус",
        max_length=20,
        choices=STATUS_CHOICES,
        default='black'
    )
    score = models.PositiveIntegerField(null=True, blank=True, verbose_name="Оценка")
    teacher_comment = models.TextField(blank=True, verbose_name="Комментарий преподавателя")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    class Meta:
        verbose_name = "Домашнее задание"
        verbose_name_plural = "Домашние задания"
        unique_together = ('lesson', 'student')
        ordering = ['-submitted_at']

    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.lesson}"


class HomeworkFile(models.Model):
    submission = models.ForeignKey(HomeworkSubmission, related_name='homework_files', on_delete=models.CASCADE)
    file = models.FileField(upload_to='homeworks/')



class Attendance(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='attendances')
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='attendances')
    STATUS_CHOICES = [
        ('0', 'Отсутствовал'),
        ('1', 'Присутствовал'),
        ('online', 'Онлайн'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    class Meta:
        verbose_name = "Посещаемость"
        verbose_name_plural = "Посещаемости"
        unique_together = ('lesson', 'student')



class Expense(models.Model):
    """Модель для учета расходов"""
    CATEGORIES = [
        ('salary', 'Зарплата'),
        ('rent', 'Аренда'),
        ('marketing', 'Маркетинг'),
        ('office', 'Хозяйственные'),
        ('other', 'Другое'),
    ]
    
    category = models.CharField(max_length=10, choices=CATEGORIES, verbose_name="Категория")
    description = models.CharField(max_length=255, verbose_name="Статья расхода")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    date = models.DateField(verbose_name="Дата")
    teacher = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, 
                              limit_choices_to={'role': 'Teacher'}, verbose_name="Преподаватель")
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    
    class Meta:
        verbose_name = "Расход"
        verbose_name_plural = "Расходы"
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.get_category_display()} - {self.amount} сом ({self.date})"


class TeacherPayment(models.Model):
    """Модель для выплат преподавателям"""
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, 
                              limit_choices_to={'role': 'Teacher'}, verbose_name="Преподаватель")
    lessons_count = models.PositiveIntegerField(verbose_name="Занятий")
    rate = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ставка")
    payment = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Выплата")
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Бонус")
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Выплачено")
    date = models.DateField(verbose_name="Дата расчета")
    is_paid = models.BooleanField(default=False, verbose_name="Оплачено")
    
    class Meta:
        verbose_name = "Выплата преподавателю"
        verbose_name_plural = "Выплаты преподавателям"
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.teacher.get_full_name()} - {self.payment} сом"
    
    @property
    def balance(self):
        return self.payment + self.bonus - self.paid_amount
    




class Invoice(models.Model):
    PAYMENT_TYPES = [
        ('cash', 'Наличные'),
        ('transfer', 'Перевод'),
        ('online', 'Онлайн'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('partial', 'Частично оплачено'),
        ('paid', 'Оплачено'),
    ]

    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, 
                              limit_choices_to={'role': 'Student'},
                              verbose_name="Ученик")
    months = models.ForeignKey(Months, on_delete=models.PROTECT, verbose_name="Месяц")
    amount = models.DecimalField(max_digits=10, decimal_places=2,
                               verbose_name="Сумма")
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                 verbose_name="Скидка")
    date_created = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")
    due_date = models.DateField(verbose_name="Срок оплаты")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES,
                            default='pending', verbose_name="Статус")
    comment = models.TextField(blank=True, verbose_name="Комментарий")

    def __str__(self):
        return f"{self.student.get_full_name()} ({self.months})"

    class Meta:
        verbose_name = "Счёт"
        verbose_name_plural = "Счета"
        ordering = ['-date_created']

    @property
    def final_amount(self):
        return self.amount - self.discount

    @property
    def paid_amount(self):
        total_expr = ExpressionWrapper(
            F('cash_amount') + F('transfer_amount') + F('online_amount'),
            output_field=DecimalField()
        )
        return self.payments.aggregate(total=Sum(total_expr))['total'] or 0

    @property
    def balance(self):
        return self.final_amount - self.paid_amount

    def update_status(self):
        if self.paid_amount >= self.final_amount:
            self.status = 'paid'
        elif self.paid_amount > 0:
            self.status = 'partial'
        else:
            self.status = 'pending'
        self.save(update_fields=['status'])
    
    def clean(self):
        if not self.student_id:
            raise ValidationError("Счет должен быть привязан к студенту")
        if self.student.role != 'Student':
            raise ValidationError("Указанный пользователь не является студентом")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class Payment(models.Model):
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name="Счёт"
    )
    cash_amount = models.DecimalField(
        max_digits=1000, decimal_places=2, default=0,
        verbose_name="Оплата наличными"
    )
    transfer_amount = models.DecimalField(
        max_digits=1000, decimal_places=2, default=0,
        verbose_name="Оплата переводом"
    )
    online_amount = models.DecimalField(
        max_digits=1000, decimal_places=2, default=0,
        verbose_name="Оплата онлайн"
    )
    date = models.DateTimeField(default=timezone.now, verbose_name="Дата оплаты")
    comment = models.TextField(blank=True, verbose_name="Комментарий")

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
        ordering = ['-date']

    def __str__(self):
        return f"Наличные: {self.cash_amount}, Перевод: {self.transfer_amount}, Онлайн: {self.online_amount}"

    @property
    def total_amount(self):
        return (self.cash_amount or 0) + (self.transfer_amount or 0) + (self.online_amount or 0)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.invoice.update_status()



class FinancialReport(models.Model):
    REPORT_TYPES = [
        ('daily', 'Ежедневный'),
        ('weekly', 'Еженедельный'),
        ('monthly', 'Ежемесячный'),
        ('yearly', 'Ежегодный'),
    ]

    report_type = models.CharField(max_length=10, choices=REPORT_TYPES,
                                 verbose_name="Тип отчёта")
    start_date = models.DateField(verbose_name="Начало периода")
    end_date = models.DateField(verbose_name="Конец периода")
    generated_at = models.DateTimeField(auto_now_add=True,
                                     verbose_name="Сгенерирован")

    class Meta:
        verbose_name = "Финансовый отчёт"
        verbose_name_plural = "Финансовые отчёты"
        ordering = ['-generated_at']


class Classroom(models.Model):
    number = models.CharField(max_length=10, unique=True, verbose_name="Номер кабинета")
    capacity = models.PositiveIntegerField(verbose_name="Вместимость")
    
    class Meta:
        verbose_name = "Кабинет"
        verbose_name_plural = "Кабинеты"
    
    def __str__(self):
        return f"Каб. {self.number}"

class Schedule(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.PROTECT, verbose_name="Кабинет")
    group = models.ForeignKey(Group, on_delete=models.PROTECT, verbose_name="Группа")
    teacher = models.ForeignKey(CustomUser, on_delete=models.PROTECT, 
                              limit_choices_to={'role': 'Teacher'},
                              verbose_name="Преподаватель")
    start_time = models.TimeField(verbose_name="Время начала")
    end_time = models.TimeField(verbose_name="Время окончания")
    date = models.DateField(verbose_name="Дата занятия")
    note = models.TextField(blank=True, verbose_name="Примечание")
    
    class Meta:
        verbose_name = "Занятие в расписании"
        verbose_name_plural = "Расписание занятий"
        ordering = ['date', 'start_time']
    
    def __str__(self):
        return f"{self.group} - {self.get_teacher_name()} - {self.date} {self.start_time}-{self.end_time}"
    
    def get_teacher_name(self):
        return f"{self.teacher.last_name} {self.teacher.first_name[0]}."
    



class Lead(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новые'),
        ('in_progress', 'В работе'),
        ('registered', 'Записан'),
        ('rejected', 'Отказ'),
    ]
    
    name = models.CharField(max_length=255, verbose_name="Имя")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    course = models.CharField(max_length=255, verbose_name="Курс")
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='new',
        verbose_name="Статус"
    )
    source = models.CharField(max_length=100, verbose_name="Источник")
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    next_contact_date = models.DateTimeField(null=True, blank=True, verbose_name="Дата следующего контакта")

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.course} ({self.get_status_display()})"
    



class PaymentNotification(models.Model):
    title = models.CharField(max_length=255, verbose_name="Заголовок уведомления")
    message_text = models.TextField(verbose_name="Текст обращения")
    extra_message = models.TextField(blank=True, null=True, verbose_name="Дополнительное обращение")


    class Meta:
        verbose_name = "Уведомление о платежах"
        verbose_name_plural = "Уведомления о платежах"

    def __str__(self):
        return self.title



class DiscountRegulation(models.Model):
    discount_amount = models.CharField(max_length=255, verbose_name="Сумма скидки(сом)")
    homework_points = models.CharField(max_length=255, verbose_name="Баллы за ДЗ")
    min_attendance = models.CharField(max_length=255, verbose_name="Минимальное кол-во посещений")

    class Meta:
        verbose_name = "Регламент скидок"
        verbose_name_plural = "Регламенты скидок"

    def __str__(self):
        return F"Сумма скидки {self.discount_amount} - Баллы за ДЗ {self.homework_points} - Минимальное кол-во посещений {self.min_attendance}"



