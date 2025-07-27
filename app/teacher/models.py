from django.db import models
from app.users.models import CustomUser

class HomeworkSubmission(models.Model):
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "Ученик"},
        related_name="homework_submissions",
        verbose_name="Ученик"
    )
    lesson = models.ForeignKey(
        'students.Lesson',
        on_delete=models.CASCADE,
        verbose_name="Урок"
    )
    comment = models.TextField(blank=True, verbose_name="Комментарий ученика")
    link = models.URLField(blank=True, null=True, verbose_name="Ссылка на задание")
    file = models.FileField(upload_to='homework_files/', blank=True, null=True, verbose_name="Файл с заданием")
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата отправки")

    score = models.CharField(max_length=10, blank=True, verbose_name="Оценка")
    teacher_comment = models.TextField(blank=True, verbose_name="Комментарий преподавателя")
    reviewed = models.BooleanField(default=False, verbose_name="Проверено")
    reviewed_at = models.DateTimeField(blank=True, null=True, verbose_name="Дата проверки")
    reviewed_by = models.ForeignKey(
        CustomUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={"role": "Преподаватель"},
        related_name="reviewed_homeworks",
        verbose_name="Проверено преподавателем"
    )

    class Meta:
        verbose_name = "Домашнее задание"
        verbose_name_plural = "Домашние задания"
        unique_together = ('student', 'lesson')
        ordering = ['-submitted_at']

    def __str__(self):
        return f'{self.student.get_full_name()} - {self.lesson}'


class Group(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Название группы")
    teacher = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={"role": "Преподаватель"},
        verbose_name="Преподаватель"
    )
    status = models.CharField(
        max_length=20,
        choices=[("active", "Активная"), ("inactive", "Неактивная")],
        verbose_name="Статус"
    )
    format = models.CharField(
        max_length=20,
        choices=[("online", "Онлайн"), ("offline", "Оффлайн")],
        verbose_name="Формат обучения"
    )
    age_group = models.CharField(max_length=50, verbose_name="Возрастная группа")
    created_at = models.DateField(auto_now_add=True, verbose_name="Дата создания")
    comment = models.TextField(blank=True, verbose_name="Комментарий")

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self):
        return self.name
