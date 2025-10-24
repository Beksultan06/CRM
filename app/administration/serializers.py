from rest_framework import serializers
import datetime
from django.utils import timezone
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
import uuid 
from PIL import Image
import io
from django.core.files.base import ContentFile

from app.administration.models import (
    Direction, Group, Teacher, Student, Lesson, Attendance, Payment, 
    Months, TeacherPayment, Expense, Invoice,
    FinancialReport, Schedule, Classroom, Lead, HomeworkSubmission, 
    PaymentNotification, DiscountRegulation, HomeworkFile
    )
from app.users.models import CustomUser
import base64
import uuid
from django.core.files.base import ContentFile

class Base64FileField(serializers.FileField):
    """
    Принимает base64 строку (с префиксом data: или без него) и конвертирует её в файл.
    """
    def to_internal_value(self, data):
        import base64, uuid
        from django.core.files.base import ContentFile

        # Если пришла строка
        if isinstance(data, str):
            # убираем префикс если есть
            if "base64," in data:
                header, base64_data = data.split("base64,", 1)
                file_ext = header.split("/")[-1].replace(";", "") or "bin"
            else:
                base64_data = data
                file_ext = "bin"

            try:
                decoded_file = base64.b64decode(base64_data)
            except Exception:
                raise serializers.ValidationError("Некорректная base64 строка.")

            file_name = str(uuid.uuid4())[:12]
            complete_file_name = f"{file_name}.{file_ext}"
            data = ContentFile(decoded_file, name=complete_file_name)

        return super().to_internal_value(data)


class FlexibleFileField(serializers.FileField):
    """Поддерживает как обычные файлы (multipart/form-data), так и base64"""
    def to_internal_value(self, data):
        # Если пришёл список файлов (например, JSON-массив base64 строк)
        if isinstance(data, list):
            files = []
            for item in data:
                if item is None:
                    continue
                files.append(self._handle_file(item))
            return files

        if data is None:
            return []

        # Один файл или одна base64 строка
        return self._handle_file(data)

    def _handle_file(self, data):
        # Если это уже файл (TemporaryUploadedFile)
        if hasattr(data, "read"):
            return super().to_internal_value(data)

        # Если это base64 строка
        if isinstance(data, str) and ";base64," in data:
            try:
                format, imgstr = data.split(";base64,")
                ext = format.split("/")[-1]
                file_name = f"{uuid.uuid4().hex}.{ext}"
                return ContentFile(base64.b64decode(imgstr), name=file_name)
            except Exception:
                raise serializers.ValidationError("Некорректный base64 файл")

        raise serializers.ValidationError("Ожидается файл или base64 строка")




class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'age', 'telegram', 'is_active', 'role']

class DirectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direction
        fields = ['id', 'name']

class GroupShortSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Group
        fields = ['id', 'group_name']

class LessonSerializer(serializers.ModelSerializer):
    homework_files = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = '__all__'

    def get_homework_files(self, obj):
        request = self.context.get('request')
        if request and obj.homework_files:
            return request.build_absolute_uri(obj.homework_files.url)
        return None



class HomeworkSubmissionSerializer(serializers.ModelSerializer):
    project_links = serializers.ListField(
        child=serializers.URLField(),
        max_length=5,
        allow_empty=False
    )
    files = serializers.ListField(
        child=serializers.FileField(),
        max_length=5,
        required=False,
        allow_empty=True
    )

    teacher_name = serializers.SerializerMethodField(read_only=True)
    group_name = serializers.SerializerMethodField(read_only=True)
    student_name = serializers.SerializerMethodField(read_only=True)  # <-- добавили

    class Meta:
        model = HomeworkSubmission
        fields = [
            'id',
            'lesson',
            'student',
            'student_name',   # <-- добавили
            'submitted_at',
            'status',
            'score',
            'teacher_comment',
            'project_links',
            'files',
            'teacher_name',
            'group_name',
        ]

    def get_teacher_name(self, obj):
        try:
            teacher = obj.lesson.month.group.teacher
            if teacher:
                return teacher.get_full_name()
        except AttributeError:
            return None

    def get_group_name(self, obj):
        try:
            return obj.lesson.month.group.group_name
        except AttributeError:
            return None

    def get_student_name(self, obj):
        try:
            return obj.student.get_full_name()
        except AttributeError:
            return None

class MonthsSerializer(serializers.ModelSerializer):
    lessons = serializers.SerializerMethodField()

    class Meta:
        model = Months
        fields = '__all__'

    def get_lessons(self, obj):
        request = self.context.get('request')
        return LessonSerializer(
            obj.lessons.all().order_by('order'),
            many=True,
            context={'request': request}  # 👈 прокидываем
        ).data



class GroupSerializer(serializers.ModelSerializer):
    direction = DirectionSerializer()
    teacher = CustomUserSerializer(read_only=True)
    students = CustomUserSerializer(many=True, read_only=True)
    months = MonthsSerializer(many=True, read_only=True)
    current_month = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Group
        fields = '__all__'

class CSVStringOrListField(serializers.ListField):
    child = serializers.CharField(allow_blank=False)

    def to_internal_value(self, data):
        if isinstance(data, str):
            # "пн,ср,пт" -> ["пн","ср","пт"]
            data = [part.strip() for part in data.split(",") if part.strip()]
        return super().to_internal_value(data)

class GroupCreateSerializer(serializers.ModelSerializer):
    # Явно валидируем по ролям
    teacher = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(role='Teacher'),
        required=False, allow_null=True
    )
    students = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(role='Student'),
        many=True, required=False
    )
    direction = serializers.PrimaryKeyRelatedField(
        queryset=Direction.objects.all()
    )

    # Примем schedule_days как CSV-строку или массив
    schedule_days = CSVStringOrListField(required=False)

    class Meta:
        model = Group
        fields = '__all__'
        extra_kwargs = {
            'teacher': {'required': False},
            'students': {'required': False}
        }

class AddRemoveStudentsSerializer(serializers.Serializer):
    student_ids = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=False
    )

    def validate_student_ids(self, value):
        from users.models import CustomUser
        students = CustomUser.objects.filter(id__in=value, role='Student')
        if not students.exists():
            raise serializers.ValidationError("Ни одного валидного студента не найдено")
        return value

class TeacherSerializer(serializers.ModelSerializer):
    directions = DirectionSerializer(many=True, read_only=True)
    groups = GroupShortSerializer(many=True, read_only=True)
    user = CustomUserSerializer()  # Используем существующий сериализатор пользователя
    
    # Для записи
    direction_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Direction.objects.all(),
        source='directions',
        write_only=True,
        required=False
    )
    group_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Group.objects.all(),
        source='groups',
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Teacher
        fields = [
            'id', 'user', 'payment_type', 'payment_amount', 'payment_period',
            'directions', 'groups', 'direction_ids', 'group_ids'
        ]



class TeacherCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    age = serializers.CharField(write_only=True, required=True)
    phone = serializers.CharField(write_only=True, required=False)
    telegram = serializers.CharField(write_only=True, required=False)
    
    direction_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Direction.objects.all(),
        source='directions',
        write_only=True,
        required=False
    )
    group_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Group.objects.all(),
        source='groups',
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Teacher
        fields = [
            'username', 'password', 'first_name', 'last_name', 'age',
            'phone', 'telegram', 'payment_type', 'payment_amount',
            'payment_period', 'direction_ids', 'group_ids'
        ]
    
    def create(self, validated_data):
        user_data = {
            'username': validated_data.pop('username'),
            'password': validated_data.pop('password'),
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name'),
            'age': validated_data.pop('age'),
            'phone': validated_data.pop('phone', ''),
            'telegram': validated_data.pop('telegram', ''),
            'role': 'Teacher'
        }
        
        directions = validated_data.pop('directions', [])
        groups = validated_data.pop('groups', [])
        
        user = CustomUser.objects.create_user(**user_data)
        teacher = Teacher.objects.create(user=user, **validated_data)
        
        # Установить направления
        teacher.directions.set(directions)

        # Установить группы
        teacher.groups.set(groups)

        # Обновить каждую группу, чтобы добавить преподавателя как teacher
        for group in groups:
            group.teacher = user
            group.save()

        return teacher



class StudentSerializer(serializers.ModelSerializer):
    directions = DirectionSerializer(many=True, read_only=True)
    groups = GroupShortSerializer(many=True, read_only=True)
    user = serializers.SerializerMethodField()
    
    # Для записи
    direction_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Direction.objects.all(),
        source='directions',
        write_only=True,
        required=False
    )
    group_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Group.objects.all(),
        source='groups',
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Student
        fields = ['id', 'user', 'directions', 'groups', 'direction_ids', 'group_ids']
    
    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'age': obj.user.age,
            'phone': obj.user.phone,
            'telegram': obj.user.telegram
        }





class StudentCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    full_name = serializers.CharField(write_only=True)
    phone = serializers.CharField(write_only=True, required=False)
    telegram = serializers.CharField(write_only=True, required=False)

    group_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Group.objects.all(),
        source='groups',
        write_only=True,
        required=False
    )
    direction_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Direction.objects.all(),
        source='directions',
        write_only=True,
        required=False
    )

    class Meta:
        model = Student
        fields = [
            'username', 'password', 'full_name', 'phone', 'telegram',
            'group_ids', 'direction_ids'
        ]

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Пользователь с таким username уже существует")
        return value

    def create(self, validated_data):
        full_name = validated_data.pop('full_name')
        first_name, last_name = full_name.split(' ', 1) if ' ' in full_name else (full_name, '')

        user_data = {
            'username': validated_data.pop('username'),
            'password': validated_data.pop('password'),
            'first_name': first_name,
            'last_name': last_name,
            'phone': validated_data.pop('phone', ''),
            'telegram': validated_data.pop('telegram', ''),
            'role': 'Student',
        }

        groups = validated_data.pop('groups', [])
        directions = validated_data.pop('directions', [])

        user = CustomUser.objects.create_user(**user_data)
        student = Student.objects.create(user=user)

        student.groups.set(groups)
        student.directions.set(directions)

        for group in groups:
            group.students.add(user)

        return student



class AttendanceSerializer(serializers.ModelSerializer):
    student_id = serializers.IntegerField(source='student.id', read_only=True)
    student = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), write_only=True)
    month_number = serializers.SerializerMethodField()
    group_id = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = ['id', 'student_id', 'student', 'status', 'group_id', 'month_number', 'lesson']

    def get_month_number(self, obj):
        return obj.lesson.month.month_number

    def get_group_id(self, obj):
        return obj.lesson.month.group.id

class PaymentSerializer(serializers.ModelSerializer):
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(role='Student'),
        write_only=True
    )
    student_name = serializers.CharField(source='invoice.student.get_full_name', read_only=True)
    month_name = serializers.CharField(source='invoice.months.title', read_only=True)
    total_amount = serializers.DecimalField(max_digits=10000, decimal_places=2, read_only=True)
    invoice_status = serializers.CharField(source='invoice.status', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'student_id',
            'cash_amount', 'transfer_amount', 'online_amount',
            'total_amount',
            'date', 'comment',
            'student_name',
            'month_name',
            'invoice_status',
        ]

    def create(self, validated_data):
        student = validated_data.pop('student_id')

        # Находим последний неоплаченный счёт
        invoice = Invoice.objects.filter(
            student=student
        ).exclude(status='paid').order_by('due_date').first()

        if not invoice:
            raise serializers.ValidationError(
                {"detail": f"У студента {student.get_full_name()} нет неоплаченных счетов"}
            )

        payment = Payment.objects.create(invoice=invoice, **validated_data)
        return payment



class GroupInvoiceSerializer(serializers.ModelSerializer):
    final_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    paid_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    balance = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Invoice
        fields = ['id', 'final_amount', 'paid_amount', 'balance']


class StudentDetailSerializer(serializers.ModelSerializer):
    attendances = serializers.SerializerMethodField()
    payments = serializers.SerializerMethodField()
    homework_scores = serializers.SerializerMethodField()  # <-- добавили

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'first_name', 'last_name', 'age', 'is_active',
            'attendances', 'homework_scores', 'payments'
        ]
    
    def get_attendances(self, obj):
        group = self.context.get('group')
        if not group:
            return []
        
        month_ids = group.months.values_list('id', flat=True)
        
        attendances = Attendance.objects.filter(
            student=obj,
            lesson__month_id__in=month_ids
        ).select_related('lesson__month')
        
        return AttendanceSerializer(attendances, many=True).data

    def get_homework_scores(self, obj):
        group = self.context.get('group')
        if not group:
            return []
        
        month_ids = group.months.values_list('id', flat=True)
        
        submissions = HomeworkSubmission.objects.filter(
            student=obj,
            lesson__month_id__in=month_ids
        ).select_related('lesson__month')
        
        return [
            {
                "lesson_id": sub.lesson.id,
                "lesson_title": sub.lesson.title,
                "month_number": sub.lesson.month.month_number,
                "score": sub.score,
                "status": sub.status
            }
            for sub in submissions
        ]

    def get_payments(self, obj):
        group = self.context.get('group')
        if not group:
            return []

        month_ids = group.months.values_list('id', flat=True)

        invoices = Invoice.objects.filter(
            student=obj,
            months_id__in=month_ids
        ).prefetch_related('payments')

        return GroupInvoiceSerializer(invoices, many=True).data




class GroupDashboardSerializer(serializers.ModelSerializer):
    direction = DirectionSerializer(read_only=True)
    teacher = CustomUserSerializer(read_only=True)
    students = serializers.SerializerMethodField()
    homework_files = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ['id', 'group_name', 'direction', 'teacher', 'students', 'homework_files']

    def get_students(self, obj):
        students = obj.students.all()
        serializer = StudentDetailSerializer(
            students,
            many=True,
            context={'group': obj}
        )
        return serializer.data

    def get_homework_files(self, obj):
        if not obj.homework_files:
            return None

        request = self.context.get("request")
        file_url = obj.homework_files.url
        absolute_url = request.build_absolute_uri(file_url) if request else file_url

        return {
            "path": file_url,
            "url": absolute_url
        }

class GroupTableSerializer(serializers.ModelSerializer):
    direction = serializers.CharField(source='direction.name')
    group = serializers.CharField(source='group_name')
    month = serializers.SerializerMethodField()
    lesson = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ['id', 'direction', 'group', 'month', 'lesson']

    def get_month(self, obj):
        """Определить текущий курс группы"""
        # Если курсов нет — возвращаем 1
        if not obj.months.exists():
            return 1

        # Логика определения курса — берём максимальный номер курса,
        # по которому уже есть уроки с датой
        last_month_with_lesson = (
            Months.objects.filter(group=obj, lessons__date__isnull=False)
            .order_by('-month_number')
            .first()
        )

        if last_month_with_lesson:
            return last_month_with_lesson.month_number

        # Если уроков с датой нет, берём первый курс
        return obj.months.order_by('month_number').first().month_number

    def get_lesson(self, obj):
        """Получить номер последнего пройденного урока"""
        try:
            month_ids = obj.months.values_list('id', flat=True)

            last_lesson = Lesson.objects.filter(
                month_id__in=month_ids
            ).order_by('-date', '-order').first()

            return last_lesson.order if last_lesson else 0
        except Exception as e:
            print(f"Error getting last lesson: {e}")
            return 0





class StudentTableSerializer(serializers.ModelSerializer):
    user_id = serializers.SerializerMethodField()  # ID пользователя
    full_name = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()
    direction = serializers.SerializerMethodField()
    teacher = serializers.SerializerMethodField()

    class Meta:
        model = Student 
        fields = ['user_id', 'full_name', 'group', 'direction', 'teacher']

    def get_user_id(self, obj):
        return obj.user.id  # возвращаем id пользователя

    def get_full_name(self, obj):
        return obj.user.get_full_name() or "-"

    def get_group(self, obj):
        groups = obj.groups.all()
        if groups.exists():
            return ", ".join([g.group_name for g in groups])
        return "-"

    def get_direction(self, obj):
        directions = set()
        for group in obj.groups.all():
            if group.direction:
                directions.add(group.direction.name)
        return ", ".join(directions) if directions else "-"

    def get_teacher(self, obj):
        teachers = set()
        for group in obj.groups.all():
            if group.teacher:
                teachers.add(f"{group.teacher.last_name} {group.teacher.first_name}")
        return ", ".join(teachers) if teachers else "-"

class SimpleMonthsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Months
        fields = ['id', 'month_number', 'title', 'description', 'group']


# serializers.py
class TeacherTableSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()
    directions = serializers.SerializerMethodField()
    student_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'full_name', 'groups', 'directions', 'student_count']

    def get_full_name(self, obj):
        return f"{obj.last_name} {obj.first_name}"

    def get_groups(self, obj):
        try:
            # Получаем объект Teacher через обратное отношение
            teacher = Teacher.objects.get(user=obj)
            groups = teacher.groups.all()
            return ", ".join([g.group_name for g in groups]) if groups.exists() else "-"
        except Teacher.DoesNotExist:
            return "-"

    def get_directions(self, obj):
        try:
            teacher = Teacher.objects.get(user=obj)
            directions = teacher.directions.all()
            return ", ".join([d.name for d in directions]) if directions.exists() else "-"
        except Teacher.DoesNotExist:
            return "-"

    def get_student_count(self, obj):
        try:
            teacher = Teacher.objects.get(user=obj)
            count = 0
            for group in teacher.groups.all():
                count += group.students.count()
            return count
        except Teacher.DoesNotExist:
            return 0


class InvoiceSerializer(serializers.ModelSerializer):
    student = serializers.SerializerMethodField()
    months = SimpleMonthsSerializer(read_only=True)  # Используем упрощенный месяц
    months_id = serializers.PrimaryKeyRelatedField(
        queryset=Months.objects.all(),
        source='months',
        write_only=True
    )
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(role='Student'),
        source='student',
        write_only=True,
        required=True
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    final_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    paid_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    balance = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'student', 'student_id', 'months', 'months_id', 'amount',
            'discount', 'final_amount', 'date_created', 'due_date', 'status',
            'status_display', 'paid_amount', 'balance', 'comment'
        ]

    def get_student(self, obj):
        return {
            'id': obj.student.id,
            'full_name': obj.student.get_full_name(),
            'phone': obj.student.phone
        }


class SimpleMonthsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Months
        fields = ['id', 'month_number', 'title', 'description', 'group']

class ExpenseSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    teacher_name = serializers.SerializerMethodField()

    class Meta:
        model = Expense
        fields = [
            'id', 'category', 'category_display', 'description', 'amount',
            'date', 'teacher', 'teacher_name', 'comment'
        ]

    def get_teacher_name(self, obj):
        return obj.teacher.get_full_name() if obj.teacher else None

class TeacherPaymentSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    balance = serializers.SerializerMethodField()

    class Meta:
        model = TeacherPayment
        fields = [
            'id', 'teacher', 'teacher_name', 'lessons_count', 'rate',
            'payment', 'bonus', 'paid_amount', 'balance', 'date', 'is_paid'
        ]

    def get_balance(self, obj):
        return obj.balance

class FinancialReportSerializer(serializers.ModelSerializer):
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    income_by_type = serializers.SerializerMethodField()
    expenses_by_category = serializers.SerializerMethodField()
    top_courses = serializers.SerializerMethodField()
    
    total_income = serializers.SerializerMethodField()
    total_expenses = serializers.SerializerMethodField()
    net_profit = serializers.SerializerMethodField()

    class Meta:
        model = FinancialReport
        fields = [
            'id', 'report_type', 'report_type_display', 'start_date', 'end_date',
            'generated_at', 'total_income', 'total_expenses', 'net_profit',
            'income_by_type', 'expenses_by_category', 'top_courses'
        ]

    def get_total_income(self, obj):
        total_expr = ExpressionWrapper(
            F('cash_amount') + F('transfer_amount') + F('online_amount'),
            output_field=DecimalField()
        )
        return Payment.objects.filter(
            date__date__range=[obj.start_date, obj.end_date]
        ).aggregate(total=Sum(total_expr))['total'] or 0

    def get_total_expenses(self, obj):
        return Expense.objects.filter(
            date__range=[obj.start_date, obj.end_date]
        ).aggregate(total=Sum('amount'))['total'] or 0

    def get_net_profit(self, obj):
        return self.get_total_income(obj) - self.get_total_expenses(obj)

    def get_income_by_type(self, obj):
        payments = Payment.objects.filter(
            date__date__range=[obj.start_date, obj.end_date]
        )
        return {
            'cash': float(payments.aggregate(total=Sum('cash_amount'))['total'] or 0),
            'transfer': float(payments.aggregate(total=Sum('transfer_amount'))['total'] or 0),
            'online': float(payments.aggregate(total=Sum('online_amount'))['total'] or 0)
        }

    def get_expenses_by_category(self, obj):
        expenses = Expense.objects.filter(
            date__range=[obj.start_date, obj.end_date]
        ).values('category').annotate(total=Sum('amount'))
        return {e['category']: float(e['total']) for e in expenses}

    def get_top_courses(self, obj):
        from django.db.models import Sum
        months = Invoice.objects.filter(
            date_created__date__range=[obj.start_date, obj.end_date]
        ).values('months__group__direction__name').annotate(
            total=Sum('amount')
        ).order_by('-total')[:5]
        
        return {c['months__group__direction__name']: float(c['total']) 
                for c in months if c['months__group__direction__name']}

# serializers.py
class GroupPaymentSerializer(serializers.ModelSerializer):
    final_amount = serializers.DecimalField(source='invoice.final_amount', max_digits=10, decimal_places=2)
    paid_amount = serializers.DecimalField(source='invoice.paid_amount', max_digits=10, decimal_places=2)
    balance = serializers.DecimalField(source='invoice.balance', max_digits=10, decimal_places=2)
    payment_type_display = serializers.CharField(source='get_payment_type_display', read_only=True)
    student_name = serializers.CharField(source='invoice.student.get_full_name', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'final_amount', 'paid_amount', 'balance',
            'payment_type', 'payment_type_display', 'date', 'comment', 'student_name'
        ]




class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = ['id', 'number', 'capacity']

class ScheduleSerializer(serializers.ModelSerializer):
    classroom = ClassroomSerializer(read_only=True)
    classroom_id = serializers.PrimaryKeyRelatedField(
        queryset=Classroom.objects.all(),
        source='classroom',
        write_only=True
    )
    teacher_name = serializers.CharField(source='get_teacher_name', read_only=True)
    group_name = serializers.CharField(source='group.group_name', read_only=True)
    
    class Meta:
        model = Schedule
        fields = [
            'id', 'classroom', 'classroom_id', 'group', 'group_name', 
            'teacher', 'teacher_name', 'start_time', 'end_time', 
            'date', 'note'
        ]
    
    def validate(self, data):
        # Проверка на пересечение времени в одном кабинете
        if Schedule.objects.filter(
            classroom=data['classroom'],
            date=data['date'],
            start_time__lt=data['end_time'],
            end_time__gt=data['start_time']
        ).exists():
            raise serializers.ValidationError("Кабинет уже занят в это время")
        
        # Проверка что преподаватель не ведет другое занятие в это время
        if Schedule.objects.filter(
            teacher=data['teacher'],
            date=data['date'],
            start_time__lt=data['end_time'],
            end_time__gt=data['start_time']
        ).exists():
            raise serializers.ValidationError("Преподаватель уже занят в это время")
        
        return data

class DailyScheduleSerializer(serializers.Serializer):
    date = serializers.DateField()
    classrooms = serializers.SerializerMethodField()
    
    def get_classrooms(self, obj):
        date = obj['date']
        classrooms = Classroom.objects.all()
        schedule = Schedule.objects.filter(date=date).select_related('classroom', 'group', 'teacher')
        
        result = []
        for classroom in classrooms:
            classroom_data = ClassroomSerializer(classroom).data
            classroom_data['schedule'] = []
            
            for hour in range(9, 21):  # С 9:00 до 20:00
                time_slot = {
                    'time': f"{hour}:00",
                    'lesson': None
                }
                
                for lesson in schedule:
                    if lesson.classroom == classroom:
                        lesson_start = lesson.start_time.hour
                        lesson_end = lesson.end_time.hour
                        
                        if hour >= lesson_start and hour < lesson_end:
                            time_slot['lesson'] = {
                                'id': lesson.id,
                                'group': lesson.group.group_name,
                                'teacher': lesson.get_teacher_name(),
                                'note': lesson.note
                            }
                            break
                
                classroom_data['schedule'].append(time_slot)
            
            result.append(classroom_data)
        
        return result
    


class ScheduleListSerializer(serializers.ModelSerializer):
    classroom_id = serializers.IntegerField(source='classroom.id')
    time = serializers.SerializerMethodField()
    roomIndex = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    direction = serializers.CharField(source='group.direction.name')
    teacher = serializers.SerializerMethodField()
    group = serializers.CharField(source='group.group_name')
    
    class Meta:
        model = Schedule
        fields = [
            'id', 'classroom_id', 'time', 'roomIndex', 
            'duration', 'direction', 'teacher', 'group',
            'date', 'note'
        ]
    
    def get_time(self, obj):
        return obj.start_time.strftime('%H:%M')
    
    def get_roomIndex(self, obj):
        return obj.classroom.id - 1  # или своя логика индекса кабинета
    
    def get_duration(self, obj):
        return (obj.end_time.hour - obj.start_time.hour)
    
    def get_teacher(self, obj):
        return f"{obj.teacher.last_name} {obj.teacher.first_name[0]}."

class ScheduleCreateSerializer(serializers.ModelSerializer):
    classroom_id = serializers.IntegerField()
    teacher = serializers.CharField()
    group = serializers.CharField()

    class Meta:
        model = Schedule
        fields = ['classroom_id', 'teacher', 'group', 'start_time', 'end_time', 'date', 'note']

    def validate(self, data):
        # Найти кабинет
        try:
            classroom = Classroom.objects.get(id=data['classroom_id'])
        except Classroom.DoesNotExist:
            raise serializers.ValidationError({"classroom_id": "Класс с таким ID не найден."})
        
        # Найти учителя
        try:
            last_name, first_initial = data['teacher'].split(' ')
            first_name = first_initial.rstrip('.')
            teacher = CustomUser.objects.get(last_name=last_name, first_name__startswith=first_name)
        except (CustomUser.DoesNotExist, ValueError):
            raise serializers.ValidationError({"teacher": "Учитель не найден или неверный формат имени."})
        
        # Найти группу
        try:
            group = Group.objects.get(group_name=data['group'])
        except Group.DoesNotExist:
            raise serializers.ValidationError({"group": "Группа не найдена."})

        # Проверка пересечения времени в кабинете
        if Schedule.objects.filter(
            classroom=classroom,
            date=data['date'],
            start_time__lt=data['end_time'],
            end_time__gt=data['start_time']
        ).exists():
            raise serializers.ValidationError("Кабинет уже занят в это время.")

        # Проверка занятости учителя
        if Schedule.objects.filter(
            teacher=teacher,
            date=data['date'],
            start_time__lt=data['end_time'],
            end_time__gt=data['start_time']
        ).exists():
            raise serializers.ValidationError("Учитель уже занят в это время.")

        data['classroom_obj'] = classroom
        data['teacher_obj'] = teacher
        data['group_obj'] = group
        return data

    def create(self, validated_data):
        classroom = validated_data.pop('classroom_obj')
        teacher = validated_data.pop('teacher_obj')
        group = validated_data.pop('group_obj')

        # Удаляем поля, которые больше не нужны
        validated_data.pop('classroom_id')
        validated_data.pop('teacher')
        validated_data.pop('group')

        return Schedule.objects.create(
            classroom=classroom,
            teacher=teacher,
            group=group,
            **validated_data
        )


    
class LeadSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_at = serializers.DateTimeField(format='%d.%m.%Y %H:%M')
    updated_at = serializers.DateTimeField(format='%d.%m.%Y %H:%M')
    next_contact_date = serializers.DateTimeField(format='%d.%m.%Y %H:%M', required=False, allow_null=True)

    class Meta:
        model = Lead
        fields = [
            'id', 'name', 'phone', 'email', 'course', 'status', 'status_display',
            'source', 'comment', 'created_at', 'updated_at', 'next_contact_date'
        ]


class ActiveStudentsSerializer(serializers.Serializer):
    active_today = serializers.IntegerField()
    new_this_week = serializers.IntegerField()
    left_this_week = serializers.IntegerField()
    avg_age = serializers.DecimalField(max_digits=4, decimal_places=1)
    directions_distribution = serializers.DictField()

class MonthlyIncomeSerializer(serializers.Serializer):
    month = serializers.CharField()
    income = serializers.DecimalField(max_digits=10, decimal_places=0)

class TeacherWorkloadSerializer(serializers.Serializer):
    teacher = serializers.CharField()
    lessons_count = serializers.IntegerField()
    students_count = serializers.IntegerField()
    group_income = serializers.DecimalField(max_digits=10, decimal_places=0)

class PopularCoursesSerializer(serializers.Serializer):
    rank = serializers.IntegerField()
    course = serializers.CharField()
    students_count = serializers.IntegerField()
    groups_count = serializers.IntegerField()
    income = serializers.DecimalField(max_digits=10, decimal_places=0)
    


class StudentAttendanceSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()
    subject = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    teacher = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'date', 'subject', 'status', 'status_display',
            'teacher', 'group'
        ]
    
    def get_date(self, obj):
        schedule = Schedule.objects.filter(
            group=obj.lesson.month.group,
            date=obj.lesson.date
        ).first()
        return schedule.date.strftime('%d.%m.%Y') if schedule else None
    
    def get_subject(self, obj):
        return obj.lesson.month.group.direction.name
    
    def get_status_display(self, obj):
        return obj.get_status_display()
    
    def get_teacher(self, obj):
        schedule = Schedule.objects.filter(
            group=obj.lesson.month.group,
            date=obj.lesson.date
        ).first()
        return schedule.teacher if schedule else None
    
    def get_group(self, obj):
        return obj.lesson.month.group.group_name

class LeadStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ['status', 'comment', 'next_contact_date']



class DashboardStatsSerializer(serializers.Serializer):
    # Новые ученики
    new_students_24h = serializers.IntegerField()
    new_students_week = serializers.IntegerField()
    new_students_month = serializers.IntegerField()
    new_students_year = serializers.IntegerField()
    
    # Последние лиды
    recent_invoices = serializers.ListField(child=serializers.DictField())
    
    # Оплаты
    payments_today = serializers.DictField()
    payments_by_method = serializers.DictField()
    
    # Занятия
    upcoming_classes = serializers.ListField(child=serializers.DictField())
    
    # Посещаемость
    attendance_stats = serializers.DictField(child=serializers.IntegerField())






class PaymentNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentNotification
        fields = '__all__'



class ProfileSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    avatarka = serializers.FileField(required=False, allow_null=True)
    avatarka_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'first_name', 'last_name',
            'telegram', 'phone', 'age', 'email',
            'password', 'avatarka', 'avatarka_url', 'role'
        ]
        extra_kwargs = {
            'username': {'read_only': True},
            'role': {'read_only': True},
        }

    def update(self, instance, validated_data):
        # смена пароля
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)

        # обновление аватарки с конвертацией в webp
        avatarka = validated_data.pop('avatarka', None)
        if avatarka is not None:
            try:
                image = Image.open(avatarka).convert("RGB")
                buffer = io.BytesIO()
                image.save(buffer, format="WEBP", quality=80)  # качество можно менять
                file_name = avatarka.name.rsplit('.', 1)[0] + ".webp"
                instance.avatarka.save(file_name, ContentFile(buffer.getvalue()), save=False)
            except Exception as e:
                raise serializers.ValidationError({"avatarka": f"Ошибка обработки изображения: {e}"})

        return super().update(instance, validated_data)

    def get_avatarka_url(self, obj):
        request = self.context.get('request')
        if obj.avatarka and hasattr(obj.avatarka, 'url') and request:
            return request.build_absolute_uri(obj.avatarka.url)
        return None
    


class StudentProfileSerializer(serializers.ModelSerializer):
    teacher = serializers.SerializerMethodField()
    direction = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True, required=False)
    avatarka = serializers.FileField(required=False, allow_null=True)
    avatarka_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'first_name', 'last_name', 'username',
            'telegram', 'phone', 'teacher', 'direction',
            'password', 'avatarka', 'avatarka_url'
        ]
        extra_kwargs = {
            'username': {'read_only': True}
        }

    def update(self, instance, validated_data):
        # обработка пароля
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)

        # обработка аватарки
        avatarka = validated_data.pop('avatarka', None)
        if avatarka is not None:
            instance.avatarka = avatarka

        return super().update(instance, validated_data)

    def get_teacher(self, obj):
        group = obj.student_groups.first()
        return group.teacher.get_full_name() if group and group.teacher else None

    def get_direction(self, obj):
        group = obj.student_groups.first()
        return group.direction.name if group and group.direction else None

    def get_avatarka_url(self, obj):
        request = self.context.get('request')
        if obj.avatarka and hasattr(obj.avatarka, 'url') and request:
            return request.build_absolute_uri(obj.avatarka.url)
        return None




class TeacherProfileSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    avatarka = serializers.FileField(required=False, allow_null=True)
    avatarka_url = serializers.SerializerMethodField(read_only=True)

    groups = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Group.objects.all(),
        required=False,
        source="teacher_add.groups"  
    )
    directions = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Direction.objects.all(),
        required=False,
        source="teacher_add.directions"
    )

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "first_name",
            "last_name",
            "username",
            "telegram",
            "phone",
            "age",
            "password",
            "avatarka",
            "avatarka_url",
            "groups",
            "directions",
        ]
        extra_kwargs = {
            "username": {"read_only": True}
        }

    def update(self, instance, validated_data):
        # обновляем пароль
        password = validated_data.pop("password", None)
        if password:
            instance.set_password(password)

        # обновляем аватарку
        avatarka = validated_data.pop("avatarka", None)
        if avatarka is not None:
            instance.avatarka = avatarka

        # работаем с Teacher
        teacher_data = validated_data.pop("teacher_add", {})
        teacher_obj, created = Teacher.objects.get_or_create(user=instance)

        groups = teacher_data.get("groups", None)
        if groups is not None:
            teacher_obj.groups.set(groups)

        directions = teacher_data.get("directions", None)
        if directions is not None:
            teacher_obj.directions.set(directions)

        teacher_obj.save()

        return super().update(instance, validated_data)

    def get_avatarka_url(self, obj):
        request = self.context.get("request")
        if obj.avatarka and hasattr(obj.avatarka, "url") and request:
            return request.build_absolute_uri(obj.avatarka.url)
        return None




class StudentHomeworkSerializer(serializers.ModelSerializer):
    homework_submission = serializers.SerializerMethodField()
    group_name = serializers.CharField(source='month.group.group_name', read_only=True)
    month_number = serializers.IntegerField(source='month.month_number', read_only=True)
    month_title = serializers.CharField(source='month.title', read_only=True)
    teacher_full_name = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'description', 'date',
            'lesson_links', 'homework_links', 'lesson_recording',
            'homework_deadline', 'homework_description', 'homework_requirements',
            'group_name', 'month_number', 'month_title',
            'teacher_full_name', 'homework_submission'
        ]

    def get_teacher_full_name(self, obj):
        teacher = getattr(obj.month.group, 'teacher', None)
        return teacher.get_full_name() if teacher else None

    def get_homework_submission(self, obj):
        request = self.context.get('request')
        user = request.user
        submission, created = HomeworkSubmission.objects.get_or_create(
            lesson=obj,
            student=user,
            defaults={"status": "black", "project_links": []}
        )
        return {
            "id": submission.id,
            "project_links": submission.project_links or [],
            "files": [
                request.build_absolute_uri(f.file.url) for f in submission.homework_files.all()
            ],
            "status": submission.status,
            "score": submission.score,
            "teacher_comment": submission.teacher_comment or "",
            "submitted_at": submission.submitted_at,
            "updated_at": submission.updated_at,
        }





class HomeworkSubmissionUpdateSerializer(serializers.ModelSerializer):
    project_links = serializers.ListField(child=serializers.URLField(), required=False)
    files = serializers.ListField(child=Base64FileField(), required=False, write_only=True)

    class Meta:
        model = HomeworkSubmission
        fields = ['project_links', 'files', 'status']

    def update(self, instance, validated_data):
        files = validated_data.pop('files', None)
        if files is not None:
            instance.homework_files.all().delete()
            for f in files:
                HomeworkFile.objects.create(submission=instance, file=f)

        project_links = validated_data.get('project_links')
        if project_links is not None:
            instance.project_links = project_links

        instance.status = 'orange'
        instance.save()
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['files'] = [f.file.url for f in instance.homework_files.all()]
        return data



class StudentProgressSerializer(serializers.Serializer):
    lesson_id = serializers.IntegerField(source='lesson.id')
    lesson_title = serializers.CharField(source='lesson.title')
    date = serializers.DateTimeField(source='lesson.date')
    attendance_status = serializers.CharField(source='attendance.status', default='0')
    homework_status = serializers.CharField(source='homework.status', default='black')
    homework_score = serializers.IntegerField(source='homework.score', default=None)

class DiscountRegulationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountRegulation
        fields = "__all__"


class UpcomingPaymentNotificationSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    student_full_name = serializers.CharField()
    due_date = serializers.DateField()
    amount_to_pay = serializers.DecimalField(max_digits=10, decimal_places=2)
    message_text = serializers.CharField()
    extra_message = serializers.CharField(allow_blank=True, required=False)