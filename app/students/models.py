from django.conf import settings
from django.db import models, transaction
from django.utils import timezone
from app.users.models import CustomUser
from app.students.querysets import *
from app.teacher.models import Group

from .constants import WeekDay

class TimeStampedModel(models.Model):
    """Абстрактная базовая модель для добавления созданных/обновленных временных меток."""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        abstract = True

class Course(TimeStampedModel):
    """Предмет или курс обучения."""
    name = models.CharField(max_length=120, unique=True, verbose_name="Название курса")
    short_code = models.CharField(max_length=20, unique=True, verbose_name="Код курса")

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def __str__(self):
        return self.name

class Classroom(models.Model):
    """Физическое расположение класса."""
    label = models.CharField(max_length=10, unique=True, verbose_name="Метка аудитории")

    class Meta:
        verbose_name = "Аудитория"
        verbose_name_plural = "Аудитории"

    def __str__(self):
        return self.label

class Lesson(TimeStampedModel):
    """Отдельный урок."""
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="lessons", verbose_name="Курс")
    teacher = models.ForeignKey(CustomUser, on_delete=models.PROTECT, limit_choices_to={"role": "Преподаватель"}, verbose_name="Преподаватель")
    classroom = models.ForeignKey(Classroom, on_delete=models.PROTECT, verbose_name="Аудитория")

    date = models.DateField(db_index=True, verbose_name="Дата")
    start_time = models.TimeField(verbose_name="Время начала")
    end_time = models.TimeField(verbose_name="Время окончания")

    group_name = models.CharField(max_length=50, blank=True, help_text="Название учебной группы", verbose_name="Название группы")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="lessons", null=True, verbose_name="Группа")

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ("date", "start_time")
        constraints = [
            models.UniqueConstraint(fields=("teacher", "date", "start_time"), name="uq_teacher_timeslot"),
            models.UniqueConstraint(fields=("classroom", "date", "start_time"), name="uq_room_timeslot"),
        ]

    def __str__(self):
        return f"{self.course.short_code} {self.date} {self.start_time}"

class Enrollment(TimeStampedModel):
    """Запись ученика на курс."""
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="enrollments", limit_choices_to={"role": "Ученик"}, verbose_name="Ученик")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments", verbose_name="Курс")
    group_name = models.CharField(max_length=50, blank=True, verbose_name="Название группы")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="enrollments", null=True, verbose_name="Группа")
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления", null=True, blank=True)

    class Meta:
        verbose_name = "Запись на курс"
        verbose_name_plural = "Записи на курсы"
        unique_together = ("student", "course")

class Attendance(TimeStampedModel):
    """Учет посещаемости учеников."""
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="attendances", limit_choices_to={"role": "Ученик"}, verbose_name="Ученик")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="attendances", verbose_name="Урок")
    attended = models.BooleanField(default=False, verbose_name="Присутствовал")
    status = models.CharField(max_length=50, choices=[
        ('attended', 'Присутствовал'),
        ('absent', 'Отсутствовал'),
        ('late', 'Опоздал'),
    ])

    objects = AttendanceQuerySet.as_manager()

    class Meta:
        verbose_name = "Посещаемость"
        verbose_name_plural = "Посещаемости"
        unique_together = ("student", "lesson")
        indexes = [models.Index(fields=("student", "lesson"))]

class Homework(TimeStampedModel):
    """Оценка домашнего задания ученика."""
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="homeworks", limit_choices_to={"role": "Ученик"}, verbose_name="Ученик")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="homeworks", verbose_name="Урок")
    score = models.PositiveSmallIntegerField(verbose_name="Оценка")

    objects = HomeworkQuerySet.as_manager()

    class Meta:
        verbose_name = "Домашнее задание"
        verbose_name_plural = "Домашние задания"
        unique_together = ("student", "lesson")
        ordering = ("-created_at",)

class Curriculum(TimeStampedModel):
    """Учебная программа по курсу и месяцам."""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="curricula", verbose_name="Курс")
    month_number = models.PositiveSmallIntegerField(verbose_name="Месяц (номер)")
    title = models.CharField(max_length=255, verbose_name="Название программы")
    lessons_outline = models.JSONField(help_text="Список тем / описаний уроков", verbose_name="План уроков")

    class Meta:
        verbose_name = "Учебная программа"
        verbose_name_plural = "Учебные программы"
        unique_together = ("course", "month_number")
        ordering = ("course", "month_number")

class DiscountPolicy(models.Model):
    """Политика скидок на основе успеваемости и посещаемости."""
    min_homework_score = models.PositiveSmallIntegerField(verbose_name="Мин. балл за ДЗ")
    max_homework_score = models.PositiveSmallIntegerField(verbose_name="Макс. балл за ДЗ")
    min_attendance = models.PositiveSmallIntegerField(verbose_name="Мин. посещаемость (%)")
    discount_amount = models.PositiveIntegerField(verbose_name="Скидка (сом)")

    class Meta:
        verbose_name = "Скидочная политика"
        verbose_name_plural = "Скидочные политики"

    def __str__(self):
        return f"{self.discount_amount} сом: {self.min_homework_score}-{self.max_homework_score} баллов, ≥{self.min_attendance}% посещений"
