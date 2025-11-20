"""
Order Fulfillment & Shipping Documents
- Pick List
- Packing Slip
- Shipping Label
- Bill of Lading (BOL)
- Shipment Confirmation
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, KeepTogether
from io import BytesIO
from datetime import datetime
from typing import List, Dict, Any
from .document_service import DocumentGenerator, format_datetime, format_date


class PickListDocument(DocumentGenerator):
    """Pick List for warehouse picking operations"""

    def generate_pdf(self, pick_data: Dict[str, Any]) -> bytes:
        """
        Generate Pick List PDF

        Args:
            pick_data: {
                'order_number': str,
                'pick_date': datetime,
                'picker': str (optional),
                'priority': str (optional),
                'items': [{
                    'sku': str,
                    'name': str,
                    'quantity': int,
                    'location': str,
                    'lot_number': str (optional),
                    'picked_qty': int (optional)
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
            "PICK LIST",
            self.styles['CustomTitle']
        ))
        elements.append(Spacer(1, 0.2*inch))

        # Order info
        info_data = {
            'Order Number': pick_data['order_number'],
            'Pick Date': format_datetime(pick_data['pick_date']),
        }
        if pick_data.get('picker'):
            info_data['Assigned To'] = pick_data['picker']
        if pick_data.get('priority'):
            info_data['Priority'] = pick_data['priority'].upper()

        elements.append(self._create_info_table(info_data))
        elements.append(Spacer(1, 0.3*inch))

        # Pick items table
        elements.append(Paragraph("Items to Pick", self.styles['CustomHeader']))
        elements.append(Spacer(1, 0.1*inch))

        table_data = [[
            Paragraph('<b>☐</b>', self.styles['InfoText']),  # Checkbox
            Paragraph('<b>SKU</b>', self.styles['InfoText']),
            Paragraph('<b>Material Name</b>', self.styles['InfoText']),
            Paragraph('<b>Location</b>', self.styles['InfoText']),
            Paragraph('<b>Lot#</b>', self.styles['InfoText']),
            Paragraph('<b>Qty</b>', self.styles['InfoText']),
            Paragraph('<b>Picked</b>', self.styles['InfoText']),
        ]]

        for item in pick_data['items']:
            table_data.append([
                Paragraph('☐', self.styles['SmallText']),
                Paragraph(item['sku'], self.styles['SmallText']),
                Paragraph(item['name'], self.styles['SmallText']),
                Paragraph(item['location'], self.styles['SmallText']),
                Paragraph(item.get('lot_number', 'ANY'), self.styles['SmallText']),
                Paragraph(str(item['quantity']), self.styles['SmallText']),
                Paragraph('_____', self.styles['SmallText']),
            ])

        table = Table(table_data, colWidths=[0.4*inch, 0.8*inch, 2*inch, 1*inch, 0.9*inch, 0.6*inch, 0.7*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (5, 1), (6, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))

        # Notes
        if pick_data.get('notes'):
            elements.append(Paragraph("<b>Notes:</b>", self.styles['CustomHeader']))
            elements.append(Paragraph(pick_data['notes'], self.styles['InfoText']))
            elements.append(Spacer(1, 0.2*inch))

        # Signature
        elements.append(Spacer(1, 0.5*inch))
        sig_table_data = [
            [Paragraph('<b>Picked By:</b>', self.styles['InfoText']),
             Paragraph('<b>Date/Time:</b>', self.styles['InfoText'])],
            ['_____________________', '_____________________'],
            [Paragraph('Signature', self.styles['SmallText']), ''],
        ]
        sig_table = Table(sig_table_data, colWidths=[2.5*inch, 2*inch])
        elements.append(sig_table)

        # Build PDF
        doc.build(elements, onFirstPage=self._create_footer, onLaterPages=self._create_footer)

        buffer.seek(0)
        return buffer.getvalue()


class PackingSlipDocument(DocumentGenerator):
    """Packing Slip for shipments"""

    def generate_pdf(self, packing_data: Dict[str, Any]) -> bytes:
        """
        Generate Packing Slip PDF

        Args:
            packing_data: {
                'order_number': str,
                'packing_date': datetime,
                'ship_to': {
                    'name': str,
                    'address_line1': str,
                    'address_line2': str (optional),
                    'city': str,
                    'state': str,
                    'postal_code': str,
                    'country': str
                },
                'items': [{
                    'sku': str,
                    'name': str,
                    'quantity': int,
                    'lot_number': str (optional)
                }],
                'tracking_number': str (optional),
                'carrier': str (optional)
            }
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # Header
        elements.extend(self._create_header())

        # Document title
        elements.append(Paragraph(
            "PACKING SLIP",
            self.styles['CustomTitle']
        ))
        elements.append(Spacer(1, 0.2*inch))

        # Order info
        info_data = {
            'Order Number': packing_data['order_number'],
            'Packing Date': format_datetime(packing_data['packing_date']),
        }
        if packing_data.get('tracking_number'):
            info_data['Tracking Number'] = packing_data['tracking_number']
        if packing_data.get('carrier'):
            info_data['Carrier'] = packing_data['carrier']

        elements.append(self._create_info_table(info_data))
        elements.append(Spacer(1, 0.3*inch))

        # Ship To Address
        elements.append(Paragraph("Ship To:", self.styles['CustomHeader']))
        ship_to = packing_data['ship_to']
        address_lines = [
            ship_to['name'],
            ship_to['address_line1'],
        ]
        if ship_to.get('address_line2'):
            address_lines.append(ship_to['address_line2'])
        address_lines.append(f"{ship_to['city']}, {ship_to['state']} {ship_to['postal_code']}")
        address_lines.append(ship_to['country'])

        for line in address_lines:
            elements.append(Paragraph(line, self.styles['InfoText']))

        elements.append(Spacer(1, 0.3*inch))

        # Items table
        elements.append(Paragraph("Package Contents", self.styles['CustomHeader']))
        elements.append(Spacer(1, 0.1*inch))

        table_data = [[
            Paragraph('<b>SKU</b>', self.styles['InfoText']),
            Paragraph('<b>Material Name</b>', self.styles['InfoText']),
            Paragraph('<b>Lot Number</b>', self.styles['InfoText']),
            Paragraph('<b>Quantity</b>', self.styles['InfoText']),
        ]]

        for item in packing_data['items']:
            table_data.append([
                Paragraph(item['sku'], self.styles['SmallText']),
                Paragraph(item['name'], self.styles['SmallText']),
                Paragraph(item.get('lot_number', '-'), self.styles['SmallText']),
                Paragraph(str(item['quantity']), self.styles['SmallText']),
            ])

        # Total
        total_qty = sum(item['quantity'] for item in packing_data['items'])
        table_data.append([
            Paragraph('<b>TOTAL</b>', self.styles['InfoText']),
            '',
            '',
            Paragraph(f'<b>{total_qty}</b>', self.styles['InfoText']),
        ])

        table = Table(table_data, colWidths=[1.2*inch, 3*inch, 1.3*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (3, 1), (3, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f5f5f5')]),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        elements.append(table)

        # Build PDF
        doc.build(elements, onFirstPage=self._create_footer, onLaterPages=self._create_footer)

        buffer.seek(0)
        return buffer.getvalue()


class ShippingLabelDocument(DocumentGenerator):
    """Shipping Label"""

    def generate_pdf(self, label_data: Dict[str, Any]) -> bytes:
        """
        Generate Shipping Label PDF

        Args:
            label_data: {
                'tracking_number': str,
                'carrier': str,
                'service_level': str,
                'ship_date': datetime,
                'from_address': {
                    'name': str,
                    'address_line1': str,
                    'city': str,
                    'state': str,
                    'postal_code': str
                },
                'to_address': {
                    'name': str,
                    'address_line1': str,
                    'address_line2': str (optional),
                    'city': str,
                    'state': str,
                    'postal_code': str,
                    'country': str
                },
                'weight': float (optional),
                'dimensions': str (optional)
            }
        """
        buffer = BytesIO()
        # Use smaller page size for label (4x6 inches is common)
        from reportlab.lib.pagesizes import landscape
        label_size = (6*inch, 4*inch)
        doc = SimpleDocTemplate(buffer, pagesize=label_size,
                               leftMargin=0.3*inch, rightMargin=0.3*inch,
                               topMargin=0.3*inch, bottomMargin=0.3*inch)
        elements = []

        # Carrier and Service
        carrier_style = self.styles['CustomTitle']
        elements.append(Paragraph(
            f"<b>{label_data['carrier']}</b>",
            carrier_style
        ))
        elements.append(Paragraph(
            label_data['service_level'],
            self.styles['CustomHeader']
        ))
        elements.append(Spacer(1, 0.1*inch))

        # Tracking number with barcode
        if label_data.get('tracking_number'):
            # Generate barcode
            barcode_img = self._generate_barcode(label_data['tracking_number'])
            if barcode_img:
                elements.append(barcode_img)
            elements.append(Paragraph(
                f"<b>{label_data['tracking_number']}</b>",
                self.styles['InfoText']
            ))
        elements.append(Spacer(1, 0.15*inch))

        # FROM Address
        elements.append(Paragraph("<b>FROM:</b>", self.styles['CustomHeader']))
        from_addr = label_data['from_address']
        elements.append(Paragraph(from_addr['name'], self.styles['InfoText']))
        elements.append(Paragraph(from_addr['address_line1'], self.styles['SmallText']))
        elements.append(Paragraph(
            f"{from_addr['city']}, {from_addr['state']} {from_addr['postal_code']}",
            self.styles['SmallText']
        ))
        elements.append(Spacer(1, 0.15*inch))

        # TO Address (larger, emphasized)
        elements.append(Paragraph("<b>TO:</b>", self.styles['CustomHeader']))
        to_addr = label_data['to_address']
        to_style = ParagraphStyle('ToAddress', parent=self.styles['InfoText'], fontSize=12)
        elements.append(Paragraph(f"<b>{to_addr['name']}</b>", to_style))
        elements.append(Paragraph(to_addr['address_line1'], to_style))
        if to_addr.get('address_line2'):
            elements.append(Paragraph(to_addr['address_line2'], to_style))
        elements.append(Paragraph(
            f"<b>{to_addr['city']}, {to_addr['state']} {to_addr['postal_code']}</b>",
            to_style
        ))
        elements.append(Paragraph(to_addr['country'], to_style))

        # Weight and dimensions if provided
        if label_data.get('weight') or label_data.get('dimensions'):
            elements.append(Spacer(1, 0.1*inch))
            weight_info = []
            if label_data.get('weight'):
                weight_info.append(f"Weight: {label_data['weight']} lbs")
            if label_data.get('dimensions'):
                weight_info.append(f"Dim: {label_data['dimensions']}")
            elements.append(Paragraph(" | ".join(weight_info), self.styles['SmallText']))

        # Build PDF without footer
        doc.build(elements)

        buffer.seek(0)
        return buffer.getvalue()


class BillOfLadingDocument(DocumentGenerator):
    """Bill of Lading (BOL)"""

    def generate_pdf(self, bol_data: Dict[str, Any]) -> bytes:
        """
        Generate Bill of Lading PDF

        Args:
            bol_data: {
                'bol_number': str,
                'shipment_date': datetime,
                'carrier': str,
                'pro_number': str (optional),
                'shipper': dict (name, address details),
                'consignee': dict (name, address details),
                'items': [{
                    'description': str,
                    'quantity': int,
                    'weight': float,
                    'class': str (optional)
                }],
                'special_instructions': str (optional)
            }
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # Header
        elements.extend(self._create_header())

        # Document title
        elements.append(Paragraph(
            "BILL OF LADING",
            self.styles['CustomTitle']
        ))
        elements.append(Spacer(1, 0.2*inch))

        # BOL info
        info_data = {
            'BOL Number': bol_data['bol_number'],
            'Shipment Date': format_datetime(bol_data['shipment_date']),
            'Carrier': bol_data['carrier'],
        }
        if bol_data.get('pro_number'):
            info_data['PRO Number'] = bol_data['pro_number']

        elements.append(self._create_info_table(info_data))
        elements.append(Spacer(1, 0.3*inch))

        # Shipper and Consignee side by side
        shipper = bol_data['shipper']
        consignee = bol_data['consignee']

        addr_table_data = [
            [Paragraph('<b>SHIPPER:</b>', self.styles['CustomHeader']),
             Paragraph('<b>CONSIGNEE:</b>', self.styles['CustomHeader'])],
            [Paragraph(shipper['name'], self.styles['InfoText']),
             Paragraph(consignee['name'], self.styles['InfoText'])],
            [Paragraph(shipper['address_line1'], self.styles['SmallText']),
             Paragraph(consignee['address_line1'], self.styles['SmallText'])],
            [Paragraph(f"{shipper['city']}, {shipper['state']} {shipper['postal_code']}", self.styles['SmallText']),
             Paragraph(f"{consignee['city']}, {consignee['state']} {consignee['postal_code']}", self.styles['SmallText'])],
        ]

        addr_table = Table(addr_table_data, colWidths=[3.25*inch, 3.25*inch])
        addr_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(addr_table)
        elements.append(Spacer(1, 0.3*inch))

        # Items
        elements.append(Paragraph("Shipment Details", self.styles['CustomHeader']))
        elements.append(Spacer(1, 0.1*inch))

        table_data = [[
            Paragraph('<b>Description</b>', self.styles['InfoText']),
            Paragraph('<b>Quantity</b>', self.styles['InfoText']),
            Paragraph('<b>Weight (lbs)</b>', self.styles['InfoText']),
            Paragraph('<b>Class</b>', self.styles['InfoText']),
        ]]

        total_weight = 0
        for item in bol_data['items']:
            table_data.append([
                Paragraph(item['description'], self.styles['SmallText']),
                Paragraph(str(item['quantity']), self.styles['SmallText']),
                Paragraph(f"{item['weight']:.2f}", self.styles['SmallText']),
                Paragraph(item.get('class', '-'), self.styles['SmallText']),
            ])
            total_weight += item['weight']

        # Total
        table_data.append([
            Paragraph('<b>TOTAL</b>', self.styles['InfoText']),
            '',
            Paragraph(f'<b>{total_weight:.2f}</b>', self.styles['InfoText']),
            '',
        ])

        table = Table(table_data, colWidths=[3*inch, 1*inch, 1.2*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (2, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f5f5f5')]),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))

        # Special Instructions
        if bol_data.get('special_instructions'):
            elements.append(Paragraph("<b>Special Instructions:</b>", self.styles['CustomHeader']))
            elements.append(Paragraph(bol_data['special_instructions'], self.styles['InfoText']))
            elements.append(Spacer(1, 0.2*inch))

        # Signatures
        elements.append(Spacer(1, 0.5*inch))
        sig_table_data = [
            [Paragraph('<b>Shipper Signature:</b>', self.styles['InfoText']), '',
             Paragraph('<b>Carrier Signature:</b>', self.styles['InfoText']), ''],
            ['_____________________', '',  '_____________________', ''],
            [Paragraph('Date:', self.styles['SmallText']), '__________',
             Paragraph('Date:', self.styles['SmallText']), '__________'],
        ]
        sig_table = Table(sig_table_data, colWidths=[1.5*inch, 1*inch, 1.5*inch, 1*inch])
        elements.append(sig_table)

        # Build PDF
        doc.build(elements, onFirstPage=self._create_footer, onLaterPages=self._create_footer)

        buffer.seek(0)
        return buffer.getvalue()
