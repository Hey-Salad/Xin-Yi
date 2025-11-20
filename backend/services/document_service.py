"""
WMS Document Generation Service
Professional PDF documents for warehouse operations
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    PageBreak, Image
)
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime
from typing import Dict, List, Any, Optional
from io import BytesIO
import qrcode
import barcode
from barcode.writer import ImageWriter


class DocumentGenerator:
    """Base class for WMS document generation"""

    def __init__(self, company_name: str = "Xin Yi WMS", company_info: Optional[Dict] = None):
        self.company_name = company_name
        self.company_info = company_info or {}
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Header style
        self.styles.add(ParagraphStyle(
            name='CustomHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))

        # Info style
        self.styles.add(ParagraphStyle(
            name='InfoText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
        ))

        # Small text
        self.styles.add(ParagraphStyle(
            name='SmallText',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#666666'),
        ))

    def _generate_qr_code(self, data: str, size: int = 100) -> Image:
        """Generate QR code image"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=1,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to BytesIO
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        return Image(buffer, width=size, height=size)

    def _generate_barcode(self, code: str, barcode_type: str = 'code128') -> Optional[Image]:
        """Generate barcode image"""
        try:
            buffer = BytesIO()
            barcode_class = barcode.get_barcode_class(barcode_type)
            barcode_instance = barcode_class(code, writer=ImageWriter())
            barcode_instance.write(buffer)
            buffer.seek(0)

            return Image(buffer, width=2.5*inch, height=0.75*inch)
        except Exception as e:
            print(f"Barcode generation error: {e}")
            return None

    def _create_header(self) -> List:
        """Create document header with company info"""
        elements = []

        # Company name
        elements.append(Paragraph(
            f"<b>{self.company_name}</b>",
            self.styles['CustomTitle']
        ))

        # Company details
        if self.company_info:
            info_text = "<br/>".join([
                self.company_info.get('address', ''),
                self.company_info.get('phone', ''),
                self.company_info.get('email', ''),
            ])
            if info_text.strip():
                elements.append(Paragraph(info_text, self.styles['SmallText']))

        elements.append(Spacer(1, 0.3*inch))

        return elements

    def _create_footer(self, canvas_obj, doc):
        """Create document footer"""
        canvas_obj.saveState()

        # Page number
        page_num = canvas_obj.getPageNumber()
        text = f"Page {page_num}"
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.drawRightString(doc.width + doc.leftMargin, 0.5*inch, text)

        # Timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        canvas_obj.drawString(doc.leftMargin, 0.5*inch, f"Generated: {timestamp}")

        # Branding
        canvas_obj.setFillColor(colors.HexColor('#999999'))
        canvas_obj.drawCentredString(
            doc.width/2 + doc.leftMargin,
            0.3*inch,
            "Powered by Xin Yi WMS - HeySalad Platform"
        )

        canvas_obj.restoreState()

    def _format_currency(self, amount: float, currency: str = 'CNY') -> str:
        """Format currency amount"""
        if currency == 'CNY':
            return f"¥{amount:,.2f}"
        elif currency == 'USD':
            return f"${amount:,.2f}"
        else:
            return f"{amount:,.2f} {currency}"

    def _create_info_table(self, data: Dict[str, str], columns: int = 2) -> Table:
        """Create a key-value information table"""
        table_data = []
        items = list(data.items())

        for i in range(0, len(items), columns):
            row = []
            for j in range(columns):
                if i + j < len(items):
                    key, value = items[i + j]
                    row.extend([Paragraph(f"<b>{key}:</b>", self.styles['InfoText']),
                               Paragraph(str(value), self.styles['InfoText'])])
                else:
                    row.extend(['', ''])
            table_data.append(row)

        col_widths = [1.2*inch, 2*inch] * columns

        table = Table(table_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        return table

    def generate_pdf(self, **kwargs) -> bytes:
        """Override this method in subclasses"""
        raise NotImplementedError("Subclasses must implement generate_pdf()")


def format_datetime(dt: datetime, format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """Format datetime object"""
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except:
            return dt
    return dt.strftime(format_str)


def format_date(dt: datetime) -> str:
    """Format date only"""
    return format_datetime(dt, '%Y-%m-%d')
