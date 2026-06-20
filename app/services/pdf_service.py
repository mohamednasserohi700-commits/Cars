"""
PDF Export Service using ReportLab
Arabic text support via bidi/arabic-reshaper or basic fallback
"""
import io
from datetime import datetime

try:
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_OK = True
except ImportError:
    REPORTLAB_OK = False


def _reshape(text):
    """Try to reshape Arabic text; fallback to original if libraries missing."""
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
        return get_display(arabic_reshaper.reshape(str(text)))
    except Exception:
        return str(text)


def generate_registrations_pdf(registrations):
    """Generate a PDF of registrations and return bytes."""
    if not REPORTLAB_OK:
        return None

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4),
                            rightMargin=1*cm, leftMargin=1*cm,
                            topMargin=2*cm, bottomMargin=1*cm)

    styles = getSampleStyleSheet()
    elements = []

    # Title
    title_style = ParagraphStyle('title', parent=styles['Title'], fontSize=16,
                                 spaceAfter=12, alignment=1)
    elements.append(Paragraph(_reshape('سجلات التسجيل - نظام النقل'), title_style))
    elements.append(Paragraph(_reshape(f'تاريخ الطباعة: {datetime.now().strftime("%Y-%m-%d %H:%M")}'),
                               ParagraphStyle('sub', parent=styles['Normal'], fontSize=10,
                                              spaceAfter=20, alignment=1)))

    # Headers (reversed for RTL)
    headers = ['الهاتف', 'وقت التسجيل', 'تاريخ السفر', 'الوردية', 'المحطة', 'الخط', 'الرقم العالمي', 'الاسم', '#']
    data = [[_reshape(h) for h in headers]]

    for i, r in enumerate(registrations, 1):
        row = [
            _reshape(r.phone),
            _reshape(r.registration_date.strftime('%H:%M')),
            _reshape(str(r.travel_date)),
            _reshape(r.shift),
            _reshape(r.station.name),
            _reshape(r.bus.name),
            _reshape(r.employee.global_id),
            _reshape(r.employee.name),
            str(i),
        ]
        data.append(row)

    col_widths = [2.5*cm, 2.5*cm, 2.8*cm, 2.8*cm, 3.5*cm, 4*cm, 2.8*cm, 5*cm, 1.2*cm]
    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ROWHEIGHT', (0, 0), (-1, -1), 22),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 0.5*cm))
    elements.append(Paragraph(_reshape(f'إجمالي السجلات: {len(registrations)}'),
                               ParagraphStyle('total', parent=styles['Normal'], fontSize=10)))

    doc.build(elements)
    buf.seek(0)
    return buf


def generate_employees_pdf(employees):
    """Generate a PDF of employees and return bytes."""
    if not REPORTLAB_OK:
        return None

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            rightMargin=1.5*cm, leftMargin=1.5*cm,
                            topMargin=2*cm, bottomMargin=1*cm)

    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(_reshape('قائمة الموظفين - نظام النقل'),
                               ParagraphStyle('t', parent=styles['Title'], fontSize=16,
                                              spaceAfter=20, alignment=1)))

    headers = ['الحالة', 'التابع', 'القسم', 'الاسم', 'الرقم العالمي', '#']
    data = [[_reshape(h) for h in headers]]
    for i, emp in enumerate(employees, 1):
        data.append([
            _reshape('نشط' if emp.is_active else 'غير نشط'),
            _reshape(emp.affiliate or ''),
            _reshape(emp.department or ''),
            _reshape(emp.name),
            _reshape(emp.global_id),
            str(i),
        ])

    table = Table(data, colWidths=[2.5*cm, 2.5*cm, 4*cm, 6*cm, 3*cm, 1.2*cm], repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ROWHEIGHT', (0, 0), (-1, -1), 22),
    ]))
    elements.append(table)
    doc.build(elements)
    buf.seek(0)
    return buf
