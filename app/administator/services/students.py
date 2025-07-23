from django.utils.timezone import localdate
from app.users.models import CustomUser
from app.manager.models import StudentRequest

def new_students_today():
    today = localdate()
    return StudentRequest.objects.filter(created_at__date=today).count()

def total_students():
    return CustomUser.objects.filter(role="Ученик").count()

def requests_stat():
    today = localdate()
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)

    return {
        "year": StudentRequest.objects.filter(created_at__date__gte=year_start).count(),
        "month": StudentRequest.objects.filter(created_at__date__gte=month_start).count(),
        "day": StudentRequest.objects.filter(created_at__date=today).count()
    }
