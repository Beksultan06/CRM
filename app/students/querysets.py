from django.db.models import Count, Avg, Q, F, IntegerField, ExpressionWrapper
from django.db import models

class AttendanceQuerySet(models.QuerySet):
    def for_student(self, student):
        return self.filter(student=student)

    def month(self, year: int, month: int):
        return self.filter(lesson__date__year=year, lesson__date__month=month)

    def attendance_rate(self):
        """Возвращает процент посещенных уроков внутри набора запросов."""
        return self.aggregate(
            attended=Count("pk", filter=Q(attended=True)),
            total=Count("pk")
        )

class HomeworkQuerySet(models.QuerySet):
    def for_student(self, student):
        return self.filter(student=student)

    def month(self, year: int, month: int):
        return self.filter(lesson__date__year=year, lesson__date__month=month)

    def average_score(self):
        return self.aggregate(avg=Avg("score"))