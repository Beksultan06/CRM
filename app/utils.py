from django.template.loader import render_to_string
from weasyprint import HTML
from django.conf import settings
from django.core.mail import EmailMessage
import tempfile
from django.db.models import Sum
from app.administration.models import TeacherPayment, Expense, FinancialReport
from app.administration.serializers import ExpenseSerializer, FinancialReportSerializer

def render_to_pdf(template_src, context_dict):
    html_string = render_to_string(template_src, context_dict)
    html = HTML(string=html_string, base_url=settings.BASE_DIR)

    # Создаем временный файл без блокировки
    result = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    html.write_pdf(target=result.name)
    result.seek(0)
    return result



def _to_bytes(pdf_file):
    """Преобразует результат render_to_pdf в bytes"""
    if hasattr(pdf_file, "read"):
        pdf_file.seek(0)
        return pdf_file.read()
    return pdf_file


def send_financial_reports_to_manager():
    attachments = []

    # ===== 1. Расчёты с преподавателями =====
    payments = TeacherPayment.objects.all()
    total_amount = payments.aggregate(Sum("paid_amount"))["paid_amount__sum"] or 0
    context = {"payments": payments, "total_amount": total_amount}
    pdf_file = render_to_pdf("reports/teacher_payments.html", context)
    attachments.append(("teacher_payments.pdf", _to_bytes(pdf_file), "application/pdf"))

    # ===== 3. Расходы =====
    expenses = Expense.objects.all().select_related("teacher")
    serializer = ExpenseSerializer(expenses, many=True)
    total_amount = expenses.aggregate(Sum("amount"))["amount__sum"] or 0
    context = {"expenses": serializer.data, "total_amount": total_amount}
    pdf_file = render_to_pdf("reports/expense_pdf_template.html", context)
    attachments.append(("expenses.pdf", _to_bytes(pdf_file), "application/pdf"))

    # ===== 4. Финансовый результат =====
    reports = FinancialReport.objects.all()
    serializer = FinancialReportSerializer(reports, many=True)
    context = {"reports": serializer.data}
    pdf_file = render_to_pdf("reports/financial_report_pdf_template.html", context)
    attachments.append(("financial_report.pdf", _to_bytes(pdf_file), "application/pdf"))

    # ===== Отправка письма =====
    subject = "Финансовые отчёты"
    body = (
        "Добрый день!\n\n"
        "Во вложении актуальные финансовые отчёты:\n"
        "— Расчёты с преподавателями\n"
        "— Доходы\n"
        "— Расходы\n"
        "— Финансовый результат\n\n"
        "С уважением,\nАвтоматизированная система"
    )

    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.MANAGER_EMAIL],
    )

    for filename, content, mimetype in attachments:
        email.attach(filename, content, mimetype)

    email.send()
    return True