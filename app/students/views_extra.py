from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import IsStudent
from .models import Attendance, Homework
from .models import DiscountPolicy
from .serializers import DiscountPolicySerializer

class ReportTableView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        student = request.user
        year = int(request.query_params.get("year", timezone.now().year))
        month = int(request.query_params.get("month", timezone.now().month))

        attendance = Attendance.objects.for_student(student).month(year, month)
        homework = Homework.objects.for_student(student).month(year, month)

        attendance_data = {}
        homework_data = {}

        for att in attendance:
            course = att.lesson.course.name
            attendance_data.setdefault(course, []).append(int(att.attended))

        for hw in homework:
            course = hw.lesson.course.name
            homework_data.setdefault(course, []).append(hw.score)

        return Response({
            "attendance": attendance_data,
            "homework_scores": homework_data
        })

class DiscountPolicyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        policies = DiscountPolicy.objects.all()
        serializer = DiscountPolicySerializer(policies, many=True)
        return Response(serializer.data)