from django.utils.timezone import localdate
from app.students.models import Lesson, Attendance
from app.users.models import CustomUser


def today_summary():
    today = localdate()

    # Занятия за сегодня
    lessons_today = Lesson.objects.filter(date=today)

    # Все записи посещаемости по этим занятиям
    attendance_qs = Attendance.objects.filter(lesson__in=lessons_today)

    # Присутствовали / отсутствовали
    attended = attendance_qs.filter(attended=True).count()
    absent = attendance_qs.filter(attended=False).count()

    total_lessons = lessons_today.count()
    total_students = CustomUser.objects.filter(role="Ученик").count()

    return {
        "total_lessons": total_lessons,
        "total_students": total_students,
        "attended": attended,
        "absent": absent,
        "attended_percent": round(attended / max(attended + absent, 1) * 100),
        "absent_percent": round(absent / max(attended + absent, 1) * 100)
    }
