"""
Inventory Documents
- Inventory Report
- Stock Status Report
- Cycle Count Report
- Inventory Adjustment Report
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from io import BytesIO
from datetime import datetime
from typing import List, Dict, Any
from .document_service import DocumentGenerator, format_datetime, format_date


class InventoryReportDocument(DocumentGenerator):
    """Complete Inventory Report"""

    def generate_pdf(self, inventory_data: Dict[str, Any]) -> bytes:
        """
        Generate Inventory Report PDF

        Args:
            inventory_data: {
                'report_date': datetime,
                'warehouse': str,
                'items': [{
                    'sku': str,
                    'name': str,
                    'category': str,
                    'quantity': int,
                    'unit': str,
                    'location': str,
                    'value': float (optional)
                }],
                'summary': {
                    'total_items': int,
                    'total_quantity': int,
                    'total_value': float (optional)
                }
            }
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.4*inch, leftMargin=0.75*inch, rightMargin=0.75*inch)
        elements = []

        # Header
        elements.extend(self._create_header())

        # Document title
        elements.append(Paragraph(
            "INVENTORY REPORT",
            self.styles['CustomTitle']
        ))
        elements.append(Spacer(1, 0.2*inch))

        # Report info
        info_data = {
            'Report Date': format_datetime(inventory_data['report_date']),
            'Warehouse': inventory_data.get('warehouse', 'Main Warehouse'),
        }
        elements.append(self._create_info_table(info_data))
        elements.append(Spacer(1, 0.3*inch))

        # Inventory items table
        elements.append(Paragraph("Inventory Items", self.styles['CustomHeader']))
        elements.append(Spacer(1, 0.1*inch))

        has_value = any(item.get('value') is not None for item in inventory_data['items'])

        if has_value:
            table_data = [[
                Paragraph('<b>SKU</b>', self.styles['InfoText']),
                Paragraph('<b>Material Name</b>', self.styles['InfoText']),
                Paragraph('<b>Category</b>', self.styles['InfoText']),
                Paragraph('<b>Quantity</b>', self.styles['InfoText']),
                Paragraph('<b>Unit</b>', self.styles['InfoText']),
                Paragraph('<b>Location</b>', self.styles['InfoText']),
                Paragraph('<b>Value</b>', self.styles['InfoText']),
            ]]

            for item in inventory_data['items']:
                table_data.append([
                    Paragraph(item['sku'], self.styles['SmallText']),
                    Paragraph(item['name'], self.styles['SmallText']),
                    Paragraph(item['category'], self.styles['SmallText']),
                    Paragraph(str(item['quantity']), self.styles['SmallText']),
                    Paragraph(item['unit'], self.styles['SmallText']),
                    Paragraph(item.get('location', '-'), self.styles['SmallText']),
                    Paragraph(self._format_currency(item.get('value', 0)), self.styles['SmallText']),
                ])

            table = Table(table_data, colWidths=[0.8*inch, 1.8*inch, 1*inch, 0.8*inch, 0.6*inch, 1*inch, 0.9*inch])
        else:
            table_data = [[
                Paragraph('<b>SKU</b>', self.styles['InfoText']),
                Paragraph('<b>Material Name</b>', self.styles['InfoText']),
                Paragraph('<b>Category</b>', self.styles['InfoText']),
                Paragraph('<b>Quantity</b>', self.styles['InfoText']),
                Paragraph('<b>Unit</b>', self.styles['InfoText']),
                Paragraph('<b>Location</b>', self.styles['InfoText']),
            ]]

            for item in inventory_data['items']:
                table_data.append([
                    Paragraph(item['sku'], self.styles['SmallText']),
                    Paragraph(item['name'], self.styles['SmallText']),
                    Paragraph(item['category'], self.styles['SmallText']),
                    Paragraph(str(item['quantity']), self.styles['SmallText']),
                    Paragraph(item['unit'], self.styles['SmallText']),
                    Paragraph(item.get('location', '-'), self.styles['SmallText']),
                ])

            table = Table(table_data, colWidths=[0.9*inch, 2*inch, 1.2*inch, 0.9*inch, 0.7*inch, 1.2*inch])

        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (3, 1), (3, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.white]),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))

        # Summary
        summary = inventory_data.get('summary', {})
        elements.append(Paragraph("Summary", self.styles['CustomHeader']))
        summary_data = [
            [Paragraph('<b>Total Items:</b>', self.styles['InfoText']),
             Paragraph(str(summary.get('total_items', 0)), self.styles['InfoText'])],
            [Paragraph('<b>Total Quantity:</b>', self.styles['InfoText']),
             Paragraph(str(summary.get('total_quantity', 0)), self.styles['InfoText'])],
        ]

        if has_value and summary.get('total_value'):
            summary_data.append([
                Paragraph('<b>Total Value:</b>', self.styles['InfoText']),
                Paragraph(self._format_currency(summary['total_value']), self.styles['InfoText'])
            ])

        summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
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


class StockStatusReportDocument(DocumentGenerator):
    """Stock Status Report - focusing on stock levels and alerts"""

    def generate_pdf(self, stock_data: Dict[str, Any]) -> bytes:
        """
        Generate Stock Status Report PDF

        Args:
            stock_data: {
                'report_date': datetime,
                'items': [{
                    'sku': str,
                    'name': str,
                    'quantity': int,
                    'safe_stock': int,
                    'status': str,  # 'normal', 'low', 'critical'
                    'reorder_point': int (optional)
                }]
            }
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.4*inch, leftMargin=0.75*inch, rightMargin=0.75*inch)
        elements = []

        # Header
        elements.extend(self._create_header())

        # Document title
        elements.append(Paragraph(
            "STOCK STATUS REPORT",
            self.styles['CustomTitle']
        ))
        elements.append(Spacer(1, 0.2*inch))

        # Report info
        info_data = {
            'Report Date': format_datetime(stock_data['report_date']),
        }
        elements.append(self._create_info_table(info_data))
        elements.append(Spacer(1, 0.3*inch))

        # Stock status table
        elements.append(Paragraph("Stock Levels", self.styles['CustomHeader']))
        elements.append(Spacer(1, 0.1*inch))

        table_data = [[
            Paragraph('<b>SKU</b>', self.styles['InfoText']),
            Paragraph('<b>Material Name</b>', self.styles['InfoText']),
            Paragraph('<b>Current</b>', self.styles['InfoText']),
            Paragraph('<b>Safe Stock</b>', self.styles['InfoText']),
            Paragraph('<b>Reorder</b>', self.styles['InfoText']),
            Paragraph('<b>Status</b>', self.styles['InfoText']),
        ]]

        for item in stock_data['items']:
            status = item.get('status', 'normal')
            status_color = {
                'normal': colors.HexColor('#27ae60'),
                'low': colors.HexColor('#f39c12'),
                'critical': colors.HexColor('#e74c3c')
            }.get(status, colors.black)

            status_text = status.upper()
            if item['quantity'] < item['safe_stock']:
                status_text = f"⚠ {status_text}"

            table_data.append([
                Paragraph(item['sku'], self.styles['SmallText']),
                Paragraph(item['name'], self.styles['SmallText']),
                Paragraph(str(item['quantity']), self.styles['SmallText']),
                Paragraph(str(item['safe_stock']), self.styles['SmallText']),
                Paragraph(str(item.get('reorder_point', '-')), self.styles['SmallText']),
                Paragraph(f'<font color="{status_color.hexval()}">{status_text}</font>', self.styles['SmallText']),
            ])

        table = Table(table_data, colWidths=[0.9*inch, 2.5*inch, 0.8*inch, 1*inch, 0.8*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 1), (4, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.white]),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        elements.append(table)

        # Build PDF
        doc.build(elements, onFirstPage=self._create_footer, onLaterPages=self._create_footer)

        buffer.seek(0)
        return buffer.getvalue()


class CycleCountReportDocument(DocumentGenerator):
    """Cycle Count Report"""

    def generate_pdf(self, count_data: Dict[str, Any]) -> bytes:
        """
        Generate Cycle Count Report PDF

        Args:
            count_data: {
                'count_id': str,
                'count_date': datetime,
                'counter': str,
                'location': str (optional),
                'items': [{
                    'sku': str,
                    'name': str,
                    'system_qty': int,
                    'counted_qty': int,
                    'variance': int,
                    'location': str
                }],
                'summary': {
                    'items_counted': int,
                    'variances_found': int,
                    'accuracy_rate': float
                }
            }
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.4*inch, leftMargin=0.75*inch, rightMargin=0.75*inch)
        elements = []

        # Header
        elements.extend(self._create_header())

        # Document title
        elements.append(Paragraph(
            "CYCLE COUNT REPORT",
            self.styles['CustomTitle']
        ))
        elements.append(Spacer(1, 0.2*inch))

        # Count info
        info_data = {
            'Count ID': count_data['count_id'],
            'Count Date': format_datetime(count_data['count_date']),
            'Counter': count_data.get('counter', 'N/A'),
        }
        if count_data.get('location'):
            info_data['Location'] = count_data['location']

        elements.append(self._create_info_table(info_data))
        elements.append(Spacer(1, 0.3*inch))

        # Count items table
        elements.append(Paragraph("Count Results", self.styles['CustomHeader']))
        elements.append(Spacer(1, 0.1*inch))

        table_data = [[
            Paragraph('<b>SKU</b>', self.styles['InfoText']),
            Paragraph('<b>Material Name</b>', self.styles['InfoText']),
            Paragraph('<b>System Qty</b>', self.styles['InfoText']),
            Paragraph('<b>Counted Qty</b>', self.styles['InfoText']),
            Paragraph('<b>Variance</b>', self.styles['InfoText']),
            Paragraph('<b>Location</b>', self.styles['InfoText']),
        ]]

        for item in count_data['items']:
            variance = item.get('variance', item['counted_qty'] - item['system_qty'])
            variance_color = colors.HexColor('#e74c3c') if variance != 0 else colors.black
            variance_text = f'+{variance}' if variance > 0 else str(variance)

            table_data.append([
                Paragraph(item['sku'], self.styles['SmallText']),
                Paragraph(item['name'], self.styles['SmallText']),
                Paragraph(str(item['system_qty']), self.styles['SmallText']),
                Paragraph(str(item['counted_qty']), self.styles['SmallText']),
                Paragraph(f'<font color="{variance_color.hexval()}">{variance_text}</font>',
                         self.styles['SmallText']),
                Paragraph(item.get('location', '-'), self.styles['SmallText']),
            ])

        table = Table(table_data, colWidths=[0.9*inch, 2.2*inch, 1*inch, 1*inch, 0.9*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 1), (4, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.white]),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))

        # Summary
        summary = count_data.get('summary', {})
        elements.append(Paragraph("Summary", self.styles['CustomHeader']))
        summary_data = [
            [Paragraph('<b>Items Counted:</b>', self.styles['InfoText']),
             Paragraph(str(summary.get('items_counted', 0)), self.styles['InfoText'])],
            [Paragraph('<b>Variances Found:</b>', self.styles['InfoText']),
             Paragraph(str(summary.get('variances_found', 0)), self.styles['InfoText'])],
            [Paragraph('<b>Accuracy Rate:</b>', self.styles['InfoText']),
             Paragraph(f"{summary.get('accuracy_rate', 0):.1f}%", self.styles['InfoText'])],
        ]
        summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
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
