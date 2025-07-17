from django.template.loader import render_to_string
from weasyprint import HTML
from django.conf import settings
import tempfile

def render_to_pdf(template_src, context_dict):
    html_string = render_to_string(template_src, context_dict)
    html = HTML(string=html_string, base_url=settings.BASE_DIR)
    result = tempfile.NamedTemporaryFile(delete=True, suffix=".pdf")
    html.write_pdf(target=result.name)
    result.seek(0)
    return result
