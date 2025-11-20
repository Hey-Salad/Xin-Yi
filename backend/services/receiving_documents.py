"""
Receiving Documents
- Purchase Order (PO) Receipt
- Receiving Report
- Putaway Report
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from io import BytesIO
from datetime import datetime
from typing import List, Dict, Any
from .document_service import DocumentGenerator, format_datetime, format_date


class POReceiptDocument(DocumentGenerator):
    """Purchase Order Receipt Document"""

    def generate_pdf(self, po_data: Dict[str, Any]) -> bytes:
        """
        Generate PO Receipt PDF

        Args:
            po_data: {
                'po_number': str,
                'vendor': str,
                'received_date': datetime,
                'receiver': str,
                'items': [{
                    'sku': str,
                    'name': str,
                    'ordered_qty': int,
                    'received_qty': int,
                    'lot_number': str,
                    'expiration_date': str,
                    'condition': str
                }],
                'notes': str (optional)
            }
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # Header
        elements.extend(self._create_header())

        # Document title
        elements.append(Paragraph(
            "PURCHASE ORDER RECEIPT",
            self.styles['CustomTitle']
        ))
        elements.append(Spacer(1, 0.2*inch))

        # PO Information
        info_data = {
            'PO Number': po_data['po_number'],
            'Vendor': po_data['vendor'],
            'Received Date': format_datetime(po_data['received_date']),
            'Received By': po_data.get('receiver', 'N/A'),
        }
        elements.append(self._create_info_table(info_data))
        elements.append(Spacer(1, 0.3*inch))

        # Items table
        elements.append(Paragraph("Received Items", self.styles['CustomHeader']))
        elements.append(Spacer(1, 0.1*inch))

        table_data = [[
            Paragraph('<b>SKU</b>', self.styles['InfoText']),
            Paragraph('<b>Material Name</b>', self.styles['InfoText']),
            Paragraph('<b>Ordered</b>', self.styles['InfoText']),
            Paragraph('<b>Received</b>', self.styles['InfoText']),
            Paragraph('<b>Lot#</b>', self.styles['InfoText']),
            Paragraph('<b>Exp Date</b>', self.styles['InfoText']),
            Paragraph('<b>Condition</b>', self.styles['InfoText']),
        ]]

        for item in po_data['items']:
            table_data.append([
                Paragraph(item['sku'], self.styles['SmallText']),
                Paragraph(item['name'], self.styles['SmallText']),
                Paragraph(str(item['ordered_qty']), self.styles['SmallText']),
                Paragraph(str(item['received_qty']), self.styles['SmallText']),
                Paragraph(item.get('lot_number', '-'), self.styles['SmallText']),
                Paragraph(format_date(item.get('expiration_date', '-')), self.styles['SmallText']),
                Paragraph(item.get('condition', 'Good'), self.styles['SmallText']),
            ])

        table = Table(table_data, colWidths=[0.8*inch, 2*inch, 0.7*inch, 0.7*inch, 0.9*inch, 0.9*inch, 0.9*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 1), (3, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))

        # Notes
        if po_data.get('notes'):
            elements.append(Paragraph("<b>Notes:</b>", self.styles['CustomHeader']))
            elements.append(Paragraph(po_data['notes'], self.styles['InfoText']))
            elements.append(Spacer(1, 0.2*inch))

        # Signature section
        elements.append(Spacer(1, 0.5*inch))
        sig_table_data = [
            [Paragraph('<b>Received By:</b>', self.styles['InfoText']), '',
             Paragraph('<b>Verified By:</b>', self.styles['InfoText']), ''],
            ['_____________________', '', '_____________________', ''],
            [Paragraph('Signature', self.styles['SmallText']), '',
             Paragraph('Signature', self.styles['SmallText']), ''],
        ]
        sig_table = Table(sig_table_data, colWidths=[1.5*inch, 1*inch, 1.5*inch, 1*inch])
        elements.append(sig_table)

        # Build PDF
        doc.build(elements, onFirstPage=self._create_footer, onLaterPages=self._create_footer)

        buffer.seek(0)
        return buffer.getvalue()


class ReceivingReportDocument(DocumentGenerator):
    """Daily/Period Receiving Report"""

    def generate_pdf(self, report_data: Dict[str, Any]) -> bytes:
        """
        Generate Receiving Report PDF

        Args:
            report_data: {
                'report_date': datetime,
                'period': str (e.g., 'Daily', 'Weekly'),
                'receipts': [{
                    'po_number': str,
                    'vendor': str,
                    'items_count': int,
                    'total_quantity': int,
                    'received_time': datetime
                }],
                'summary': {
                    'total_receipts': int,
                    'total_items': int,
                    'total_quantity': int
                }
            }
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # Header
        elements.extend(self._create_header())

        # Document title
        elements.append(Paragraph(
            "RECEIVING REPORT",
            self.styles['CustomTitle']
        ))
        elements.append(Spacer(1, 0.2*inch))

        # Report info
        info_data = {
            'Report Date': format_datetime(report_data['report_date']),
            'Period': report_data.get('period', 'Daily'),
        }
        elements.append(self._create_info_table(info_data))
        elements.append(Spacer(1, 0.3*inch))

        # Receipts table
        elements.append(Paragraph("Receipts Summary", self.styles['CustomHeader']))
        elements.append(Spacer(1, 0.1*inch))

        table_data = [[
            Paragraph('<b>PO Number</b>', self.styles['InfoText']),
            Paragraph('<b>Vendor</b>', self.styles['InfoText']),
            Paragraph('<b>Items</b>', self.styles['InfoText']),
            Paragraph('<b>Total Qty</b>', self.styles['InfoText']),
            Paragraph('<b>Received Time</b>', self.styles['InfoText']),
        ]]

        for receipt in report_data['receipts']:
            table_data.append([
                Paragraph(receipt['po_number'], self.styles['SmallText']),
                Paragraph(receipt['vendor'], self.styles['SmallText']),
                Paragraph(str(receipt['items_count']), self.styles['SmallText']),
                Paragraph(str(receipt['total_quantity']), self.styles['SmallText']),
                Paragraph(format_datetime(receipt['received_time']), self.styles['SmallText']),
            ])

        table = Table(table_data, colWidths=[1.2*inch, 2*inch, 0.8*inch, 0.9*inch, 1.8*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 1), (3, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))

        # Summary
        summary = report_data.get('summary', {})
        elements.append(Paragraph("Summary", self.styles['CustomHeader']))
        summary_table_data = [
            [Paragraph('<b>Total Receipts:</b>', self.styles['InfoText']),
             Paragraph(str(summary.get('total_receipts', 0)), self.styles['InfoText'])],
            [Paragraph('<b>Total Items:</b>', self.styles['InfoText']),
             Paragraph(str(summary.get('total_items', 0)), self.styles['InfoText'])],
            [Paragraph('<b>Total Quantity:</b>', self.styles['InfoText']),
             Paragraph(str(summary.get('total_quantity', 0)), self.styles['InfoText'])],
        ]
        summary_table = Table(summary_table_data, colWidths=[2*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ecf0f1')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(summary_table)

        # Build PDF
        doc.build(elements, onFirstPage=self._create_footer, onLaterPages=self._create_footer)

        buffer.seek(0)
        return buffer.getvalue()


class PutawayReportDocument(DocumentGenerator):
    """Putaway Report - tracking where items were stored"""

    def generate_pdf(self, putaway_data: Dict[str, Any]) -> bytes:
        """
        Generate Putaway Report PDF

        Args:
            putaway_data: {
                'report_id': str,
                'date': datetime,
                'operator': str,
                'items': [{
                    'sku': str,
                    'name': str,
                    'lot_number': str,
                    'quantity': int,
                    'from_location': str,
                    'to_location': str,
                    'status': str
                }]
            }
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # Header
        elements.extend(self._create_header())

        # Document title
        elements.append(Paragraph(
            "PUTAWAY REPORT",
            self.styles['CustomTitle']
        ))
        elements.append(Spacer(1, 0.2*inch))

        # Report info
        info_data = {
            'Report ID': putaway_data['report_id'],
            'Date': format_datetime(putaway_data['date']),
            'Operator': putaway_data.get('operator', 'N/A'),
        }
        elements.append(self._create_info_table(info_data))
        elements.append(Spacer(1, 0.3*inch))

        # Putaway items table
        elements.append(Paragraph("Putaway Items", self.styles['CustomHeader']))
        elements.append(Spacer(1, 0.1*inch))

        table_data = [[
            Paragraph('<b>SKU</b>', self.styles['InfoText']),
            Paragraph('<b>Material</b>', self.styles['InfoText']),
            Paragraph('<b>Lot#</b>', self.styles['InfoText']),
            Paragraph('<b>Qty</b>', self.styles['InfoText']),
            Paragraph('<b>From</b>', self.styles['InfoText']),
            Paragraph('<b>To Location</b>', self.styles['InfoText']),
            Paragraph('<b>Status</b>', self.styles['InfoText']),
        ]]

        for item in putaway_data['items']:
            table_data.append([
                Paragraph(item['sku'], self.styles['SmallText']),
                Paragraph(item['name'], self.styles['SmallText']),
                Paragraph(item.get('lot_number', '-'), self.styles['SmallText']),
                Paragraph(str(item['quantity']), self.styles['SmallText']),
                Paragraph(item.get('from_location', 'Receiving'), self.styles['SmallText']),
                Paragraph(item['to_location'], self.styles['SmallText']),
                Paragraph(item.get('status', 'Completed'), self.styles['SmallText']),
            ])

        table = Table(table_data, colWidths=[0.7*inch, 1.5*inch, 0.8*inch, 0.5*inch, 1*inch, 1.2*inch, 0.8*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (3, 1), (3, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        elements.append(table)

        # Build PDF
        doc.build(elements, onFirstPage=self._create_footer, onLaterPages=self._create_footer)

        buffer.seek(0)
        return buffer.getvalue()
