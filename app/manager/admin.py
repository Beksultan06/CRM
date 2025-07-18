from django.contrib import admin
from .models import (
    StudentRequest,
    Payment,
    PaymentReminder,
    TeacherRate,
    TeacherBonus,
    Expense,
    Notification,
)

@admin.register(StudentRequest)
class StudentRequestAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "course", "status", "assigned_to", "created_at")
    list_filter = ("status", "assigned_to", "course", "created_at")
    search_fields = ("full_name", "phone", "email", "message")
    ordering = ("-created_at",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "total_amount", "status", "date")
    list_filter = ("status", "date", "course")
    search_fields = ("student__full_name", "course__name", "comment")
    ordering = ("-date",)


@admin.register(PaymentReminder)
class PaymentReminderAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "amount", "due_date", "created_at")
    list_filter = ("due_date", "created_at", "course")
    search_fields = ("student__full_name", "course__name", "message")
    ordering = ("-created_at",)


@admin.register(TeacherRate)
class TeacherRateAdmin(admin.ModelAdmin):
    list_display = ("teacher", "rate_per_lesson")
    list_filter = ("teacher",)
    search_fields = ("teacher__full_name",)


@admin.register(TeacherBonus)
class TeacherBonusAdmin(admin.ModelAdmin):
    list_display = ("teacher", "amount", "month")
    list_filter = ("month", "teacher")
    search_fields = ("teacher__full_name",)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("name", "amount", "category", "date")
    list_filter = ("category", "date")
    search_fields = ("name", "category")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "message", "created_at", "is_read")
    list_filter = ("is_read", "created_at")
    search_fields = ("user__full_name", "message")
    ordering = ("-created_at",)
