from django.conf import settings
from django.db import models, transaction
from django.utils import timezone
from app.users.models import CustomUser
from app.students.querysets import *

from .constants import WeekDay

class TimeStampedModel(models.Model):
    """Абстрактная базовая модель для добавления созданных/обновленных временных меток."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Course(TimeStampedModel):
    """Представляет предмет/курс (например, английский язык, робототехника)."""
    name = models.CharField(max_length=120, unique=True)
    short_code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

class Classroom(models.Model):
    """Физическое расположение класса."""
    label = models.CharField(max_length=10, unique=True)

    def __str__(self) -> str:
        return self.label

class Lesson(TimeStampedModel):
    """Отдельный экземпляр урока привязан к определенной дате и времени."""
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="lessons")
    teacher = models.ForeignKey(CustomUser, on_delete=models.PROTECT, limit_choices_to={"role": "Преподаватель"})
    classroom = models.ForeignKey(Classroom, on_delete=models.PROTECT)

    date = models.DateField(db_index=True)
    start_time = models.TimeField()
    end_time = models.TimeField()

    group_name = models.CharField(max_length=50, blank=True, help_text="Название учебной группы")

    class Meta:
        verbose_name = "Lesson"
        verbose_name_plural = "Lessons"
        ordering = ("date", "start_time")
        constraints = [
            # предотвратить повторное бронирование преподавателем или классом
            models.UniqueConstraint(fields=("teacher", "date", "start_time"), name="uq_teacher_timeslot"),
            models.UniqueConstraint(fields=("classroom", "date", "start_time"), name="uq_room_timeslot"),
        ]

    def __str__(self):
        return f"{self.course.short_code} {self.date} {self.start_time}"

class Enrollment(TimeStampedModel):
    """Связь между студентом и курсом (сквозная связь «многие ко многим»)"""
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="enrollments", limit_choices_to={"role": "Ученик"})
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    group_name = models.CharField(max_length=50, blank=True)

    class Meta:
        unique_together = ("student", "course")
        verbose_name = "Enrollment"
        verbose_name_plural = "Enrollments"

class Attendance(TimeStampedModel):
    """
Учет посещаемости занятий каждым учеником."""
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="attendances", limit_choices_to={"role": "Ученик"})
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="attendances")
    attended = models.BooleanField(default=False)

    objects = AttendanceQuerySet.as_manager()

    class Meta:
        unique_together = ("student", "lesson")
        indexes = [models.Index(fields=("student", "lesson"))]
        

class Homework(TimeStampedModel):
    """
Оценка домашнего задания за урок."""
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="homeworks", limit_choices_to={"role": "Ученик"})
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="homeworks")
    score = models.PositiveSmallIntegerField()

    objects = HomeworkQuerySet.as_manager()

    class Meta:
        unique_together = ("student", "lesson")
        ordering = ("-created_at",)

class Curriculum(TimeStampedModel):
    """Учебная программа по месяцам и курсам — сворачиваемый список в пользовательском интерфейсе."""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="curricula")
    month_number = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=255)
    lessons_outline = models.JSONField(help_text="Array of lesson titles / descriptions")

    class Meta:
        unique_together = ("course", "month_number")
        ordering = ("course", "month_number")