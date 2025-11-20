"""
WMS Document Generation Routes
Generate and download various warehouse documents
"""

from flask import Blueprint, jsonify, request, send_file
from datetime import datetime
from io import BytesIO
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.receiving_documents import (
    POReceiptDocument,
    ReceivingReportDocument,
    PutawayReportDocument
)
from services.inventory_documents import (
    InventoryReportDocument,
    StockStatusReportDocument,
    CycleCountReportDocument
)
from services.fulfillment_documents import (
    PickListDocument,
    PackingSlipDocument,
    ShippingLabelDocument,
    BillOfLadingDocument
)
from database_supabase import get_supabase_client

document_bp = Blueprint('documents', __name__, url_prefix='/api/documents')
supabase = get_supabase_client()


# Handle OPTIONS requests for CORS preflight
@document_bp.route('/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    """Handle CORS preflight requests"""
    return '', 204


# ============= RECEIVING DOCUMENTS =============

@document_bp.route('/receiving/po-receipt', methods=['POST'])
def generate_po_receipt():
    """Generate Purchase Order Receipt Document"""
    try:
        data = request.json

        # Validate required fields
        required = ['po_number', 'vendor', 'items']
        if not all(field in data for field in required):
            return jsonify({'error': 'Missing required fields'}), 400

        # Set defaults
        if 'received_date' not in data:
            data['received_date'] = datetime.now()

        # Generate PDF
        doc_generator = POReceiptDocument(
            company_name=data.get('company_name', 'Xin Yi WMS'),
            company_info=data.get('company_info', {})
        )
        pdf_bytes = doc_generator.generate_pdf(data)

        # Return PDF file
        return send_file(
            BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"PO_Receipt_{data['po_number']}_{datetime.now().strftime('%Y%m%d')}.pdf"
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@document_bp.route('/receiving/receiving-report', methods=['POST'])
def generate_receiving_report():
    """Generate Receiving Report"""
    try:
        data = request.json

        doc_generator = ReceivingReportDocument(
            company_name=data.get('company_name', 'Xin Yi WMS')
        )
        pdf_bytes = doc_generator.generate_pdf(data)

        return send_file(
            BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"Receiving_Report_{datetime.now().strftime('%Y%m%d')}.pdf"
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@document_bp.route('/receiving/putaway-report', methods=['POST'])
def generate_putaway_report():
    """Generate Putaway Report"""
    try:
        data = request.json

        doc_generator = PutawayReportDocument(
            company_name=data.get('company_name', 'Xin Yi WMS')
        )
        pdf_bytes = doc_generator.generate_pdf(data)

        return send_file(
            BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"Putaway_Report_{data['report_id']}_{datetime.now().strftime('%Y%m%d')}.pdf"
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============= INVENTORY DOCUMENTS =============

@document_bp.route('/inventory/inventory-report', methods=['POST', 'GET'])
def generate_inventory_report():
    """Generate Complete Inventory Report"""
    try:
        if request.method == 'GET':
            # Fetch all materials from database
            response = supabase.table('materials')\
                .select('id, name, sku, category, quantity, unit, location')\
                .order('name')\
                .execute()

            items = []
            for material in response.data:
                items.append({
                    'sku': material['sku'],
                    'name': material['name'],
                    'category': material['category'],
                    'quantity': material['quantity'],
                    'unit': material['unit'],
                    'location': material.get('location', 'N/A')
                })

            data = {
                'report_date': datetime.now(),
                'warehouse': 'Main Warehouse',
                'items': items,
                'summary': {
                    'total_items': len(items),
                    'total_quantity': sum(item['quantity'] for item in items)
                }
            }
        else:
            data = request.json

        doc_generator = InventoryReportDocument(
            company_name=data.get('company_name', 'Xin Yi WMS')
        )
        pdf_bytes = doc_generator.generate_pdf(data)

        return send_file(
            BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"Inventory_Report_{datetime.now().strftime('%Y%m%d')}.pdf"
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@document_bp.route('/inventory/stock-status', methods=['POST', 'GET'])
def generate_stock_status():
    """Generate Stock Status Report"""
    try:
        if request.method == 'GET':
            # Fetch materials with stock levels
            response = supabase.table('materials')\
                .select('id, name, sku, quantity, safe_stock')\
                .order('name')\
                .execute()

            items = []
            for material in response.data:
                qty = material['quantity']
                safe = material['safe_stock']

                # Determine status
                if qty >= safe:
                    status = 'normal'
                elif qty >= safe * 0.5:
                    status = 'low'
                else:
                    status = 'critical'

                items.append({
                    'sku': material['sku'],
                    'name': material['name'],
                    'quantity': qty,
                    'safe_stock': safe,
                    'reorder_point': safe,
                    'status': status
                })

            data = {
                'report_date': datetime.now(),
                'items': items
            }
        else:
            data = request.json

        doc_generator = StockStatusReportDocument(
            company_name=data.get('company_name', 'Xin Yi WMS')
        )
        pdf_bytes = doc_generator.generate_pdf(data)

        return send_file(
            BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"Stock_Status_{datetime.now().strftime('%Y%m%d')}.pdf"
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@document_bp.route('/inventory/cycle-count', methods=['POST'])
def generate_cycle_count():
    """Generate Cycle Count Report"""
    try:
        data = request.json

        # Calculate variances and accuracy
        items = data.get('items', [])
        variances = sum(1 for item in items if item.get('variance', 0) != 0)
        accuracy_rate = ((len(items) - variances) / len(items) * 100) if items else 0

        if 'summary' not in data:
            data['summary'] = {
                'items_counted': len(items),
                'variances_found': variances,
                'accuracy_rate': accuracy_rate
            }

        doc_generator = CycleCountReportDocument(
            company_name=data.get('company_name', 'Xin Yi WMS')
        )
        pdf_bytes = doc_generator.generate_pdf(data)

        return send_file(
            BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"Cycle_Count_{data['count_id']}_{datetime.now().strftime('%Y%m%d')}.pdf"
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============= FULFILLMENT & SHIPPING DOCUMENTS =============

@document_bp.route('/fulfillment/pick-list', methods=['POST'])
def generate_pick_list():
    """Generate Pick List"""
    try:
        data = request.json

        doc_generator = PickListDocument(
            company_name=data.get('company_name', 'Xin Yi WMS')
        )
        pdf_bytes = doc_generator.generate_pdf(data)

        return send_file(
            BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"Pick_List_{data['order_number']}_{datetime.now().strftime('%Y%m%d')}.pdf"
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@document_bp.route('/fulfillment/packing-slip', methods=['POST'])
def generate_packing_slip():
    """Generate Packing Slip"""
    try:
        data = request.json

        doc_generator = PackingSlipDocument(
            company_name=data.get('company_name', 'Xin Yi WMS')
        )
        pdf_bytes = doc_generator.generate_pdf(data)

        return send_file(
            BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"Packing_Slip_{data['order_number']}_{datetime.now().strftime('%Y%m%d')}.pdf"
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@document_bp.route('/fulfillment/shipping-label', methods=['POST'])
def generate_shipping_label():
    """Generate Shipping Label"""
    try:
        data = request.json

        doc_generator = ShippingLabelDocument(
            company_name=data.get('company_name', 'Xin Yi WMS')
        )
        pdf_bytes = doc_generator.generate_pdf(data)

        return send_file(
            BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"Shipping_Label_{data.get('tracking_number', 'LABEL')}_{datetime.now().strftime('%Y%m%d')}.pdf"
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@document_bp.route('/shipping/bill-of-lading', methods=['POST'])
def generate_bill_of_lading():
    """Generate Bill of Lading"""
    try:
        data = request.json

        doc_generator = BillOfLadingDocument(
            company_name=data.get('company_name', 'Xin Yi WMS')
        )
        pdf_bytes = doc_generator.generate_pdf(data)

        return send_file(
            BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"BOL_{data['bol_number']}_{datetime.now().strftime('%Y%m%d')}.pdf"
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============= DOCUMENT LIST & METADATA =============

@document_bp.route('/available', methods=['GET'])
def get_available_documents():
    """Get list of all available document types"""
    documents = {
        'receiving': [
            {
                'type': 'po_receipt',
                'name': 'Purchase Order Receipt',
                'description': 'Document confirming receipt of a purchase order',
                'endpoint': '/api/documents/receiving/po-receipt'
            },
            {
                'type': 'receiving_report',
                'name': 'Receiving Report',
                'description': 'Summary of all receipts for a period',
                'endpoint': '/api/documents/receiving/receiving-report'
            },
            {
                'type': 'putaway_report',
                'name': 'Putaway Report',
                'description': 'Tracking where received items were stored',
                'endpoint': '/api/documents/receiving/putaway-report'
            }
        ],
        'inventory': [
            {
                'type': 'inventory_report',
                'name': 'Inventory Report',
                'description': 'Complete inventory status report',
                'endpoint': '/api/documents/inventory/inventory-report'
            },
            {
                'type': 'stock_status',
                'name': 'Stock Status Report',
                'description': 'Stock levels and alerts',
                'endpoint': '/api/documents/inventory/stock-status'
            },
            {
                'type': 'cycle_count',
                'name': 'Cycle Count Report',
                'description': 'Physical count vs system inventory',
                'endpoint': '/api/documents/inventory/cycle-count'
            }
        ],
        'fulfillment': [
            {
                'type': 'pick_list',
                'name': 'Pick List',
                'description': 'List of items to pick for an order',
                'endpoint': '/api/documents/fulfillment/pick-list'
            },
            {
                'type': 'packing_slip',
                'name': 'Packing Slip',
                'description': 'Contents of a shipment',
                'endpoint': '/api/documents/fulfillment/packing-slip'
            },
            {
                'type': 'shipping_label',
                'name': 'Shipping Label',
                'description': 'Address label for shipment',
                'endpoint': '/api/documents/fulfillment/shipping-label'
            },
            {
                'type': 'bill_of_lading',
                'name': 'Bill of Lading',
                'description': 'Freight shipment documentation',
                'endpoint': '/api/documents/shipping/bill-of-lading'
            }
        ]
    }

    return jsonify(documents)
