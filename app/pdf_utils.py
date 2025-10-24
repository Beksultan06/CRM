from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from django.core.files.base import ContentFile
from django.conf import settings

def generate_receipt_pdf(payment):
    """Генерация PDF чека для платежа"""
    try:
        # Определяем способ оплаты
        payment_methods = []
        if payment.cash_amount > 0:
            payment_methods.append("Наличные")
        if payment.transfer_amount > 0:
            payment_methods.append("Банковский перевод")
        if payment.online_amount > 0:
            payment_methods.append("Онлайн")
        
        payment_method = ", ".join(payment_methods) if payment_methods else "Не указан"

        # Получаем преподавателя группы
        teacher_name = "Не указан"
        try:
            # Получаем группу из месяца счета
            group = payment.invoice.months.group
            if group.teacher:
                teacher_name = group.teacher.get_full_name()
        except Exception as e:
            print(f"Ошибка при получении преподавателя: {str(e)}")

        # Описание счета с именем преподавателя
        invoice_description = f"{payment.invoice.months.title} - {teacher_name}"

        context = {
            'payment': payment,
            'invoice_description': invoice_description,
            'total_amount': payment.total_amount,
            'payment_method': payment_method,
            'cash_amount': payment.cash_amount,
            'transfer_amount': payment.transfer_amount,
            'online_amount': payment.online_amount,
            'customer_name': payment.invoice.student.get_full_name(),
        }

        # Генерируем PDF
        html_string = render_to_string('reports/payment_receipt.html', context)
        html = HTML(string=html_string, base_url=settings.BASE_DIR)

        # Создаем временный файл
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            html.write_pdf(target=tmp_file.name)
            
            # Сохраняем файл в модели Payment
            with open(tmp_file.name, 'rb') as f:
                payment.receipt_pdf.save(
                    f'receipt_{payment.id}_{payment.date.strftime("%Y%m%d_%H%M%S")}.pdf',
                    ContentFile(f.read())
                )
        
        payment.save()
        return True
        
    except Exception as e:
        # Логируем ошибку, но не прерываем создание платежа
        print(f"Ошибка при генерации PDF чека: {str(e)}")
        return False


