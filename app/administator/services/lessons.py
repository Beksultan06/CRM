from django.utils.timezone import localdate
from app.students.models import Lesson

def today_lessons():
    today = localdate()
    result = []

    lessons = Lesson.objects.filter(date=today).select_related("course", "teacher", "group")
    for lesson in lessons:
        result.append({
            "course": lesson.course.name,
            "group": lesson.group.name if lesson.group else lesson.group_name,
            "teacher": lesson.teacher.get_full_name(),
            "time": lesson.start_time.strftime("%H:%M")
        })

    return result
