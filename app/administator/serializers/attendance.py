from rest_framework import serializers
from app.students.models import Attendance, Lesson

class AttendanceSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    lesson_date = serializers.DateField(source='lesson.date', read_only=True)

    class Meta:
        model = Attendance
        fields = ['id', 'lesson_title', 'lesson_date', 'status']
        
class LessonShortSerializer(serializers.ModelSerializer):
    course = serializers.CharField(source="course.name", read_only=True)
    group = serializers.CharField(source="group.name", read_only=True)
    classroom = serializers.CharField(source="classroom.label", read_only=True)

    class Meta:
        model = Lesson
        fields = ["id", "date", "start_time", "end_time", "course", "group", "classroom"]

class LessonSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    date = serializers.DateField()
    group = serializers.CharField()
    course = serializers.CharField()
    time = serializers.CharField()

class AttendanceStudentSerializer(serializers.ModelSerializer):
    lesson = LessonShortSerializer()

    class Meta:
        model = Attendance
        fields = ["id", "lesson", "attended", "status", "created_at"]

class AttendanceUpdateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    status = serializers.ChoiceField(choices=[
        ('attended', 'Присутствовал'),
        ('absent', 'Отсутствовал'),
        ('late', 'Опоздал')
    ])

    def validate_id(self, value):
        if not Attendance.objects.filter(id=value).exists():
            raise serializers.ValidationError("Attendance с таким ID не найден.")
        return value

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

class BulkAttendanceUpdateSerializer(serializers.Serializer):
    attendances = AttendanceUpdateSerializer(many=True)

    def save(self, **kwargs):
        for data in self.validated_data["attendances"]:
            att = Attendance.objects.get(id=data["id"])
            att.status = data["status"]
            att.save()
        return {"updated": len(self.validated_data["attendances"])}