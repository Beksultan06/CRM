from django.contrib import admin
from .models import Course, Classroom, Lesson, Enrollment, Attendance, Homework, Curriculum

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "short_code", "created_at")
    search_fields = ("name", "short_code")

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ("label",)

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("course", "date", "start_time", "end_time", "teacher", "classroom")
    list_filter = ("course", "teacher", "classroom", "date")
    search_fields = ("course__name", "teacher__username")

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "group_name")
    search_fields = ("student__username", "course__name", "group_name")

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("student", "lesson", "attended")
    list_filter = ("attended", "lesson__course")
    raw_id_fields = ("student", "lesson")

@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ("student", "lesson", "score")
    list_filter = ("lesson__course",)
    raw_id_fields = ("student", "lesson")

@admin.register(Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    list_display = ("course", "month_number", "title")
    list_filter = ("course", "month_number")
