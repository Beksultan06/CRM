from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Group, Attendance, HomeworkSubmission, CustomUser

@receiver(m2m_changed, sender=Group.students.through)
def create_attendance_and_homework(sender, instance, action, pk_set, **kwargs):
    """
    Создаёт Attendance и HomeworkSubmission для добавленных студентов
    во всех уроках группы.
    """
    if action == "post_add":  # выполняется после добавления студентов
        for student_id in pk_set:
            student = CustomUser.objects.filter(pk=student_id).first()
            if not student:
                continue

            # Проходим по всем месяцам и урокам группы
            for month in instance.months.all():  # ✅ правильный related_name
                for lesson in month.lessons.all():  # ✅ правильный related_name
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