from django.db import models
from app.users.models import CustomUser
from app.students.models import Lesson

class HomeworkSubmission(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={"role": "Ученик"})
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    comment = models.TextField(blank=True)
    link = models.URLField(blank=True, null=True)
    file = models.FileField(upload_to='homework_files/', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    score = models.CharField(max_length=10, blank=True)
    teacher_comment = models.TextField(blank=True)
    reviewed = models.BooleanField(default=False)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    reviewed_by = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.SET_NULL, limit_choices_to={"role": "Преподаватель"})

    class Meta:
        unique_together = ('student', 'lesson')
        ordering = ['-submitted_at']

    def __str__(self):
        return f'{self.student.get_full_name()} - {self.lesson}'


class Group(models.Model):
    name = models.CharField(max_length=50, unique=True)
    teacher = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, limit_choices_to={"role": "Преподаватель"})
    status = models.CharField(max_length=20, choices=[("active", "Активная"), ("inactive", "Неактивная")])
    format = models.CharField(max_length=20, choices=[("online", "Онлайн"), ("offline", "Оффлайн")])
    age_group = models.CharField(max_length=50)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name
