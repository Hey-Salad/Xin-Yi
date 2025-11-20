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
        """Setup Wise-style paragraph styles - clean, minimal, professional"""
        # Title style - Wise style, left-aligned, bold
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.black,
            spaceAfter=16,
            spaceBefore=0,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        ))

        # Header style - Wise style, clean
        self.styles.add(ParagraphStyle(
            name='CustomHeader',
            parent=self.styles['Heading2'],
            fontSize=11,
            textColor=colors.black,
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))

        # Info style - Wise style, readable
        self.styles.add(ParagraphStyle(
            name='InfoText',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.black,
            leading=12,
        ))

        # Small text - Wise style, subtle
        self.styles.add(ParagraphStyle(
            name='SmallText',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#666666'),
            leading=10,
        ))

        # Company info style
        self.styles.add(ParagraphStyle(
            name='CompanyInfo',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#333333'),
            alignment=TA_CENTER,
            leading=10,
        ))
        
        # Date/metadata style - Wise style
        self.styles.add(ParagraphStyle(
            name='MetaText',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            leading=12,
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
        """Create Wise-style header - logo LEFT-aligned at top, company info below"""
        elements = []

        # Logo FIRST - LEFT-aligned at top (directly added, no table wrapper)
        try:
            import os
            logo_path = os.path.join(os.path.dirname(__file__), 'heysalad_logo_black.png')
            if os.path.exists(logo_path):
                logo = Image(logo_path, width=1.8*inch, height=0.54*inch)
                logo.hAlign = 'LEFT'  # Force left alignment
                elements.append(logo)
                elements.append(Spacer(1, 0.05*inch))  # Reduced from 0.15 to 0.05
        except Exception as e:
            pass
        
        # Company name BELOW logo - bold, LEFT-aligned
        company_name_style = ParagraphStyle(
            'CompanyName',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.black,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold',
            spaceAfter=2,  # Reduced from 4 to 2
        )
        
        company_name = Paragraph("<b>HeySalad Payments Ltd.</b>", company_name_style)
        elements.append(company_name)
        
        # Company address details - Wise style, LEFT-aligned
        address_style = ParagraphStyle(
            'WiseAddress',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#333333'),
            alignment=TA_LEFT,
            leading=11,
        )
        
        address_details = Paragraph(
            "3rd Floor, 86-90 Paul Street<br/>"
            "London<br/>"
            "EC2A 4NE<br/>"
            "United Kingdom",
            address_style
        )
        elements.append(address_details)
        elements.append(Spacer(1, 0.25*inch))

        return elements

    def _create_footer(self, canvas_obj, doc):
        """Create Wise-style footer - minimal and clean with correct page count"""
        canvas_obj.saveState()

        # Document hash - left side, small and subtle
        import hashlib
        page_num = canvas_obj.getPageNumber()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        hash_input = f"{timestamp}-{page_num}-{self.company_name}".encode()
        doc_hash = hashlib.sha256(hash_input).hexdigest()[:24].lower()
        
        canvas_obj.setFont('Helvetica', 7)
        canvas_obj.setFillColor(colors.HexColor('#999999'))
        canvas_obj.drawString(
            doc.leftMargin,
            0.4*inch,
            f"{doc_hash}"
        )

        # Page number - right side, Wise style with actual page count
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(colors.HexColor('#666666'))
        # Use the actual page number without total for now (will show just page number)
        canvas_obj.drawRightString(
            doc.width + doc.leftMargin,
            0.4*inch,
            f"{page_num}"
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
