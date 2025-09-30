from django.contrib import admin
from .models import (
    Direction, Group, Teacher, Student, Months, Lesson,
    HomeworkSubmission, Attendance, Expense, TeacherPayment,
    Invoice, Payment, FinancialReport, Classroom, Schedule, Lead,
    PaymentNotification, DiscountRegulation, HomeworkFile
)


@admin.register(Direction)
class DirectionAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = (
        "group_name",
        "direction",
        "age_group",
        "format",
        "duration_months",
        "planned_start",
        "teacher",
        "creation_type",
        "current_course",
        "current_month",
    )
    list_filter = ("format", "direction", "creation_type", "age_group")
    search_fields = ("group_name", "direction__name", "teacher__first_name", "teacher__last_name")
    filter_horizontal = ("students",)
    readonly_fields = ("creation_date", "current_course", "current_month")
    fieldsets = (
        ("Основная информация", {
            "fields": ("group_name", "direction", "age_group", "format", "duration_months", "planned_start", "creation_date", "creation_type")
        }),
        ("Учебный процесс", {
            "fields": ("lessons_per_month", "lesson_duration", "lessons_per_week", "schedule_days")
        }),
        ("Участники", {
            "fields": ("teacher", "students")
        }),
        ("Дополнительно", {
            "fields": ("comment", "current_course", "current_month")
        }),
    )


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("user", "payment_type", "payment_amount", "payment_period")
    list_filter = ("payment_type", "payment_period")
    search_fields = ("user__first_name", "user__last_name")
    filter_horizontal = ("groups", "directions")
    autocomplete_fields = ("user",)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("user",)
    search_fields = ("user__first_name", "user__last_name")
    filter_horizontal = ("groups", "directions")
    autocomplete_fields = ("user",)


@admin.register(Months)
class MonthsAdmin(admin.ModelAdmin):
    list_display = ("group", "month_number", "title")
    list_filter = ("group",)
    search_fields = ("title",)
    autocomplete_fields = ("group",)

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("month", "title", "order", "date")
    list_filter = ("month", "date")
    search_fields = ("title",)
    autocomplete_fields = ("month",)


class HomeworkFileInline(admin.TabularInline):
    model = HomeworkFile
    extra = 1

@admin.register(HomeworkSubmission)
class HomeworkSubmissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'lesson', 'student', 'status', 'score', 'submitted_at']
    inlines = [HomeworkFileInline]  # подключаем файлы как inline
    # fields = [...]  # если тут было 'files', удалить



@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("lesson", "student", "status")
    list_filter = ("status",)
    search_fields = ("student__first_name", "student__last_name", "lesson__title")
    autocomplete_fields = ("lesson", "student")

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("category", "description", "amount", "date", "teacher")
    list_filter = ("category", "date")
    search_fields = ("description", "teacher__first_name", "teacher__last_name")
    autocomplete_fields = ("teacher",)


@admin.register(TeacherPayment)
class TeacherPaymentAdmin(admin.ModelAdmin):
    list_display = ("teacher", "lessons_count", "rate", "payment", "bonus", "paid_amount", "date", "is_paid")
    list_filter = ("is_paid", "date")
    search_fields = ("teacher__first_name", "teacher__last_name")
    autocomplete_fields = ("teacher",)



@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("student", "months", "amount", "discount", "due_date", "status")
    list_filter = ("status", "due_date")
    search_fields = ("student__first_name", "student__last_name", "months__group__group_name")
    autocomplete_fields = ("student", "months")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'invoice',
        'cash_amount',
        'transfer_amount',
        'online_amount',
        'total_amount',
        'date',
    )
    list_filter = ('date', 'invoice')
    search_fields = ('invoice__student__first_name', 'invoice__student__last_name')
    readonly_fields = ('total_amount',)
    ordering = ('-date',)

    def total_amount(self, obj):
        return obj.total_amount
    total_amount.short_description = "Общая сумма"


@admin.register(FinancialReport)
class FinancialReportAdmin(admin.ModelAdmin):
    list_display = ("report_type", "start_date", "end_date", "generated_at")
    list_filter = ("report_type", "generated_at")


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ("number", "capacity")
    search_fields = ("number",)


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ("classroom", "group", "teacher", "date", "start_time", "end_time")
    list_filter = ("date", "classroom", "teacher")
    search_fields = ("group__group_name", "teacher__first_name", "teacher__last_name")
    autocomplete_fields = ("classroom", "group", "teacher")


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "course", "status", "source", "created_at")
    list_filter = ("status", "source", "created_at")
    search_fields = ("name", "phone", "course")


@admin.register(PaymentNotification)
class PaymentNotificationAdmin(admin.ModelAdmin):
    list_display = ("recipient_name", "due_date", "amount", "created_at")
    list_filter = ("due_date", "created_at")
    search_fields = ("recipient_name",)


@admin.register(DiscountRegulation)
class DiscountRegulationAdmin(admin.ModelAdmin):
    list_display = ("discount_amount", "homework_points", "min_attendance")
    search_fields = ("discount_amount", "homework_points", "min_attendance")
    list_filter = ("discount_amount", "homework_points", "min_attendance")