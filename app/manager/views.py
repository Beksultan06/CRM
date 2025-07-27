from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import StudentRequest, Payment, PaymentReminder, TeacherRate, TeacherBonus
from app.users.models import CustomUser
from app.students.models import Lesson, Attendance, Homework
from .serializers import *
from .permissions import IsManager
from rest_framework.views import APIView
from django.db.models import Sum, Count, Q
from datetime import date
from functools import cached_property
from datetime import timedelta
from app.utils import render_to_pdf
from django.core.mail import EmailMessage
from django.conf import settings

class StudentManagerRequestViewSet(viewsets.ModelViewSet):
    queryset = StudentRequest.objects.select_related("course", "assigned_to")
    serializer_class = StudentManagerRequestSerializer
    permission_classes = [IsAuthenticated, IsManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "course"]
    search_fields = ["^full_name", "=phone", "email"]
    ordering_fields = ["created_at"]

class ManagerLessonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Lesson.objects.select_related("course", "teacher", "classroom")
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsManager]

    def get_queryset(self):
        queryset = super().get_queryset()
        date_str = self.request.query_params.get("date")
        if date_str:
            try:
                date_obj = timezone.datetime.fromisoformat(date_str).date()
                queryset = queryset.filter(date=date_obj)
            except ValueError:
                pass
        return queryset

class StudentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CustomUser.objects.filter(role="Ученик")
    serializer_class = StudentShortSerializer
    permission_classes = [IsAuthenticated, IsManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["first_name", "last_name", "phone", "telegram"]

    @action(detail=True, methods=["get"])
    def profile(self, request, pk=None):
        student = self.get_object()
        serializer = StudentProfileSerializer(student)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def attendance(self, request, pk=None):
        student = self.get_object()
        queryset = Attendance.objects.filter(student=student).select_related("lesson")
        return Response(AttendanceSerializer(queryset, many=True).data)

    @action(detail=True, methods=["get"])
    def homework(self, request, pk=None):
        student = self.get_object()
        queryset = Homework.objects.filter(student=student).select_related("lesson")
        return Response(HomeworkSerializer(queryset, many=True).data)

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related("student", "course")
    serializer_class = PaymentSerializers
    permission_classes = [IsAuthenticated, IsManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "course"]
    search_fields = ["student__first_name", "student__last_name"]
    ordering_fields = ["date", "total_amount"]

class PaymentReminderViewSet(viewsets.ModelViewSet):
    queryset = PaymentReminder.objects.select_related("student", "course")
    serializer_class = PaymentReminderSerializer
    permission_classes = [IsAuthenticated, IsManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["course"]
    search_fields = ["student__first_name", "student__last_name"]


class FinancialSummaryView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        start = request.query_params.get("start")
        end = request.query_params.get("end")
        data = calculate_financial_summary(start, end)
        return Response(FinancialSummarySerializer(data).data)

class TeacherReportView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        start = request.query_params.get("start")
        end = request.query_params.get("end")
        report = calculate_teacher_report(start, end)
        return Response(TeacherReportSerializer(report, many=True).data)

class UpcomingRemindersView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        target_date = timezone.localdate() + timedelta(days=3)
        reminders = PaymentReminder.objects.filter(due_date=target_date)
        serializer = PaymentReminderSerializer(reminders, many=True)
        return Response(serializer.data)


class FinancialSummaryPDFView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        start_date = request.query_params.get("start")
        end_date = request.query_params.get("end")
        filters = {}
        if start_date:
            filters["date__gte"] = start_date
        if end_date:
            filters["date__lte"] = end_date

        revenue = Payment.objects.filter(**filters).aggregate(total=Sum("total_amount"))["total"] or 0
        expenses = Expense.objects.filter(**filters).aggregate(total=Sum("amount"))["total"] or 0
        profit = revenue - expenses

        data = {
            "revenue": revenue,
            "expenses": expenses,
            "profit": profit,
        }

        pdf = render_to_pdf("report/summary.html", data)
        return FileResponse(pdf, as_attachment=True, filename="summary_report.pdf")


class TeacherReportPDFView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        start = request.query_params.get("start")
        end = request.query_params.get("end")
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
            bonus = TeacherBonus.objects.filter(teacher=teacher).aggregate(total=Sum("amount"))["total"] or 0
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

        pdf = render_to_pdf("report/teachers.html", {"teachers": report})
        return FileResponse(pdf, as_attachment=True, filename="teacher_report.pdf")


class DashboardSummaryView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        today = timezone.now().date()
        month_start = today.replace(day=1)

        new_requests = StudentRequest.objects.filter(created_at__gte=month_start).count()
        students_count = CustomUser.objects.filter(role="Ученик").count()
        income = Payment.objects.filter(date__gte=month_start).aggregate(total=Sum("total_amount"))['total'] or 0

        total_payments = Payment.objects.filter(date__gte=month_start).count()
        paid_payments = Payment.objects.filter(date__gte=month_start, status="paid").count()
        paid_percent = int((paid_payments / total_payments) * 100) if total_payments > 0 else 0

        return Response({
            "new_requests": new_requests,
            "students": students_count,
            "income_this_month": income,
            "payments_paid_percent": paid_percent
        })

class SendReportEmailView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        data = calculate_financial_summary(None, None)
        pdf = render_to_pdf("report/summary.html", data)
        email = EmailMessage(
            subject="Финансовый отчет",
            body="Во вложении финансовый отчет в формате PDF.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.MANAGER_EMAIL],
        )
        email.attach("summary.pdf", pdf.getvalue(), "application/pdf")
        email.send()
        return Response({"status": "sent"})