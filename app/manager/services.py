# report/services.py
from django.db.models import Sum, Q
from manager.models import Payment, Expense, TeacherBonus, TeacherRate
from app.students.models import Lesson
from app.users.models import CustomUser

def calculate_financial_summary(start=None, end=None):
    filters = {}
    if start:
        filters["date__gte"] = start
    if end:
        filters["date__lte"] = end

    revenue = Payment.objects.filter(**filters).aggregate(total=Sum("total_amount"))['total'] or 0
    expenses = Expense.objects.filter(**filters).aggregate(total=Sum("amount"))['total'] or 0
    profit = revenue - expenses
    return {
        "revenue": revenue,
        "expenses": expenses,
        "profit": profit
    }

def calculate_teacher_report(start=None, end=None):
    date_filter = Q()
    if start:
        date_filter &= Q(date__gte=start)
    if end:
        date_filter &= Q(date__lte=end)

    report = []
    teachers = CustomUser.objects.filter(role="Преподаватель")
    for teacher in teachers:
        lesson_count = Lesson.objects.filter(teacher=teacher).filter(date_filter).count()
        rate_obj = TeacherRate.objects.filter(teacher=teacher).first()
        rate = rate_obj.rate_per_lesson if rate_obj else 0
        salary = lesson_count * rate
        bonus = TeacherBonus.objects.filter(teacher=teacher).aggregate(total=Sum("amount"))['total'] or 0
        total = salary + bonus

        report.append({
            "teacher_id": teacher.id,
            "teacher_name": teacher.get_full_name(),
            "lesson_count": lesson_count,
            "rate": rate,
            "salary": salary,
            "bonus": bonus,
            "total_payout": total
        })

    return report
