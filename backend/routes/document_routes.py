"""
WMS Document Generation Routes
Generate and download various warehouse documents
"""

from flask import Blueprint, jsonify, request, send_file
from datetime import datetime, timedelta
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

@document_bp.route('/receiving/po-receipt', methods=['POST', 'GET'])
def generate_po_receipt():
    """Generate Purchase Order Receipt Document"""
    try:
        if request.method == 'GET':
            # Generate sample data from Supabase
            response = supabase.table('materials').select('*').limit(5).execute()
            items = []
            for material in response.data:
                items.append({
                    'sku': material['sku'],
                    'name': material['name'],
                    'ordered_qty': 100,
                    'received_qty': 100,
                    'lot_number': f'LOT-{datetime.now().strftime("%Y%m%d")}',
                    'expiration_date': (datetime.now().replace(day=1) + timedelta(days=90)).strftime('%Y-%m-%d'),
                    'condition': 'Good'
                })
            
            data = {
                'po_number': f'PO-{datetime.now().strftime("%Y%m%d")}',
                'vendor': 'Sample Vendor',
                'received_date': datetime.now(),
                'receiver': 'System',
                'items': items,
                'company_name': 'HeySalad - Xin Yi WMS'
            }
        else:
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


@document_bp.route('/receiving/receiving-report', methods=['POST', 'GET'])
def generate_receiving_report():
    """Generate Receiving Report"""
    try:
        if request.method == 'GET':
            # Generate sample data
            response = supabase.table('materials').select('*').limit(10).execute()
            receipts = []
            for i, material in enumerate(response.data):
                receipts.append({
                    'po_number': f'PO-{i+1:04d}',
                    'vendor': f'Vendor {i+1}',
                    'items_count': 1,
                    'total_quantity': material['quantity'],
                    'received_time': datetime.now()
                })
            
            data = {
                'report_id': f'RR-{datetime.now().strftime("%Y%m%d")}',
                'report_date': datetime.now(),
                'period': 'Daily',
                'start_date': datetime.now().replace(day=1),
                'end_date': datetime.now(),
                'receipts': receipts,
                'summary': {
                    'total_receipts': len(receipts),
                    'total_items': len(receipts),
                    'total_quantity': sum(r['total_quantity'] for r in receipts)
                },
                'company_name': 'HeySalad - Xin Yi WMS'
            }
        else:
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


@document_bp.route('/receiving/putaway-report', methods=['POST', 'GET'])
def generate_putaway_report():
    """Generate Putaway Report"""
    try:
        if request.method == 'GET':
            # Generate sample data
            response = supabase.table('materials').select('*').limit(8).execute()
            items = []
            for material in response.data:
                items.append({
                    'sku': material['sku'],
                    'name': material['name'],
                    'lot_number': f'LOT-{datetime.now().strftime("%Y%m%d")}',
                    'quantity': material['quantity'],
                    'from_location': 'Receiving',
                    'to_location': material['location'],
                    'status': 'Completed'
                })
            
            data = {
                'report_id': f'PR-{datetime.now().strftime("%Y%m%d")}',
                'date': datetime.now(),
                'operator': 'System',
                'items': items,
                'company_name': 'HeySalad - Xin Yi WMS'
            }
        else:
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


@document_bp.route('/inventory/cycle-count', methods=['POST', 'GET'])
def generate_cycle_count():
    """Generate Cycle Count Report"""
    try:
        if request.method == 'GET':
            # Generate sample data
            response = supabase.table('materials').select('*').limit(10).execute()
            items = []
            variances = 0
            for material in response.data:
                system_qty = material['quantity']
                # Simulate some variances
                counted_qty = system_qty + (1 if len(items) % 3 == 0 else 0)
                variance = counted_qty - system_qty
                if variance != 0:
                    variances += 1
                
                items.append({
                    'sku': material['sku'],
                    'name': material['name'],
                    'location': material['location'],
                    'system_qty': system_qty,
                    'counted_qty': counted_qty,
                    'variance': variance
                })
            
            accuracy_rate = ((len(items) - variances) / len(items) * 100) if items else 0
            
            data = {
                'count_id': f'CC-{datetime.now().strftime("%Y%m%d")}',
                'count_date': datetime.now(),
                'counter': 'System',
                'items': items,
                'summary': {
                    'items_counted': len(items),
                    'variances_found': variances,
                    'accuracy_rate': accuracy_rate
                },
                'company_name': 'HeySalad - Xin Yi WMS'
            }
        else:
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

@document_bp.route('/fulfillment/pick-list', methods=['POST', 'GET'])
def generate_pick_list():
    """Generate Pick List"""
    try:
        if request.method == 'GET':
            # Generate sample data
            response = supabase.table('materials').select('*').limit(6).execute()
            items = []
            for material in response.data:
                items.append({
                    'sku': material['sku'],
                    'name': material['name'],
                    'quantity': min(material['quantity'], 10),
                    'location': material['location']
                })
            
            data = {
                'order_number': f'ORD-{datetime.now().strftime("%Y%m%d-%H%M")}',
                'pick_date': datetime.now(),
                'picker': 'System',
                'priority': 'Normal',
                'items': items,
                'company_name': 'HeySalad - Xin Yi WMS'
            }
        else:
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


@document_bp.route('/fulfillment/packing-slip', methods=['POST', 'GET'])
def generate_packing_slip():
    """Generate Packing Slip"""
    try:
        if request.method == 'GET':
            # Generate sample data
            response = supabase.table('materials').select('*').limit(5).execute()
            items = []
            for material in response.data:
                items.append({
                    'sku': material['sku'],
                    'name': material['name'],
                    'quantity': min(material['quantity'], 5)
                })
            
            data = {
                'order_number': f'ORD-{datetime.now().strftime("%Y%m%d-%H%M")}',
                'packing_date': datetime.now(),
                'ship_to': {
                    'name': 'Sample Customer',
                    'address_line1': '123 Main Street',
                    'city': 'Sample City',
                    'state': 'CA',
                    'postal_code': '12345',
                    'country': 'USA'
                },
                'items': items,
                'tracking_number': f'TRK-{datetime.now().strftime("%Y%m%d%H%M")}',
                'carrier': 'Express Delivery',
                'company_name': 'HeySalad - Xin Yi WMS'
            }
        else:
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


@document_bp.route('/fulfillment/shipping-label', methods=['POST', 'GET'])
def generate_shipping_label():
    """Generate Shipping Label"""
    try:
        if request.method == 'GET':
            # Generate sample data
            data = {
                'tracking_number': f'TRK-{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'carrier': 'Express Delivery',
                'service_level': 'Next Day',
                'ship_date': datetime.now(),
                'from_address': {
                    'name': 'HeySalad Warehouse',
                    'address_line1': '123 Warehouse Road',
                    'city': 'Sample City',
                    'state': 'CA',
                    'postal_code': '12345'
                },
                'to_address': {
                    'name': 'Sample Customer',
                    'address_line1': '456 Customer Avenue',
                    'city': 'Customer City',
                    'state': 'NY',
                    'postal_code': '67890',
                    'country': 'USA'
                },
                'weight': 5.5,
                'dimensions': '12x10x8 inches',
                'company_name': 'HeySalad - Xin Yi WMS'
            }
        else:
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


@document_bp.route('/shipping/bill-of-lading', methods=['POST', 'GET'])
def generate_bill_of_lading():
    """Generate Bill of Lading"""
    try:
        if request.method == 'GET':
            # Generate sample data
            response = supabase.table('materials').select('*').limit(3).execute()
            items = []
            for material in response.data:
                items.append({
                    'description': material['name'],
                    'quantity': min(material['quantity'], 20),
                    'weight': min(material["quantity"], 20) * 0.5
                })
            
            data = {
                'bol_number': f'BOL-{datetime.now().strftime("%Y%m%d")}',
                'shipment_date': datetime.now(),
                'shipper': {
                    'name': 'HeySalad Warehouse',
                    'address_line1': '123 Warehouse Road',
                    'city': 'Sample City',
                    'state': 'CA',
                    'postal_code': '12345'
                },
                'consignee': {
                    'name': 'Sample Customer',
                    'address_line1': '456 Customer Avenue',
                    'city': 'Customer City',
                    'state': 'NY',
                    'postal_code': '67890'
                },
                'carrier': 'Express Freight',
                'items': items,
                'company_name': 'HeySalad - Xin Yi WMS'
            }
        else:
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


# ============= SIGNATURE ENDPOINTS =============

from services.signature_service import add_signature_to_pdf

def get_sample_document_data(doc_type):
    """Get sample data for document generation"""
    now = datetime.now()
    
    if doc_type in ['po-receipt', 'receiving-report', 'putaway-report']:
        return {
            'po_number': f'PO-{now.strftime("%Y%m%d")}',
            'vendor': 'Sample Vendor',
            'received_date': now,
            'items': []
        }
    elif doc_type in ['inventory-report', 'stock-status', 'cycle-count']:
        return {
            'report_date': now,
            'items': []
        }
    elif doc_type in ['pick-list', 'packing-slip', 'shipping-label']:
        return {
            'order_number': f'ORD-{now.strftime("%Y%m%d")}',
            'customer': 'Sample Customer',
            'ship_date': now,
            'items': []
        }
    return {}

@document_bp.route('/receiving/po-receipt/sign', methods=['POST'])
def sign_po_receipt():
    """Generate and sign PO Receipt"""
    try:
        data = request.json
        print(f"Received sign request: {data.keys() if data else 'No data'}")
        
        signature_data = data.get('signature')
        signer_name = data.get('signer_name')
        
        print(f"Signature data length: {len(signature_data) if signature_data else 0}")
        print(f"Signer name: {signer_name}")
        
        if not signature_data or not signer_name:
            return jsonify({'error': 'Signature and signer name required'}), 400
        
        # Generate original PDF with sample data
        print("Generating original PDF...")
        doc = POReceiptDocument()
        sample_data = get_sample_document_data('po-receipt')
        pdf_bytes = doc.generate_pdf(sample_data)
        print(f"PDF generated, size: {len(pdf_bytes)} bytes")
        
        # Add signature
        print("Adding signature to PDF...")
        signed_pdf = add_signature_to_pdf(pdf_bytes, signature_data, signer_name)
        print(f"Signed PDF created, size: {len(signed_pdf)} bytes")
        
        return send_file(
            BytesIO(signed_pdf),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'po_receipt_signed_{datetime.now().strftime("%Y%m%d")}.pdf'
        )
    except Exception as e:
        import traceback
        print(f"Error in sign_po_receipt: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500


@document_bp.route('/receiving/receiving-report/sign', methods=['POST'])
def sign_receiving_report():
    """Generate and sign Receiving Report"""
    try:
        data = request.json
        signature_data = data.get('signature')
        signer_name = data.get('signer_name')
        
        if not signature_data or not signer_name:
            return jsonify({'error': 'Signature and signer name required'}), 400
        
        doc = ReceivingReportDocument()
        sample_data = get_sample_document_data('receiving-report')
        pdf_bytes = doc.generate_pdf(sample_data)
        signed_pdf = add_signature_to_pdf(pdf_bytes, signature_data, signer_name)
        
        return send_file(
            BytesIO(signed_pdf),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'receiving_report_signed_{datetime.now().strftime("%Y%m%d")}.pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@document_bp.route('/receiving/putaway-report/sign', methods=['POST'])
def sign_putaway_report():
    """Generate and sign Putaway Report"""
    try:
        data = request.json
        signature_data = data.get('signature')
        signer_name = data.get('signer_name')
        
        if not signature_data or not signer_name:
            return jsonify({'error': 'Signature and signer name required'}), 400
        
        doc = PutawayReportDocument()
        sample_data = get_sample_document_data('putaway-report')
        pdf_bytes = doc.generate_pdf(sample_data)
        signed_pdf = add_signature_to_pdf(pdf_bytes, signature_data, signer_name)
        
        return send_file(
            BytesIO(signed_pdf),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'putaway_report_signed_{datetime.now().strftime("%Y%m%d")}.pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@document_bp.route('/inventory/inventory-report/sign', methods=['POST'])
def sign_inventory_report():
    """Generate and sign Inventory Report"""
    try:
        data = request.json
        signature_data = data.get('signature')
        signer_name = data.get('signer_name')
        
        if not signature_data or not signer_name:
            return jsonify({'error': 'Signature and signer name required'}), 400
        
        doc = InventoryReportDocument()
        sample_data = get_sample_document_data('inventory-report')
        pdf_bytes = doc.generate_pdf(sample_data)
        signed_pdf = add_signature_to_pdf(pdf_bytes, signature_data, signer_name)
        
        return send_file(
            BytesIO(signed_pdf),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'inventory_report_signed_{datetime.now().strftime("%Y%m%d")}.pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@document_bp.route('/inventory/stock-status/sign', methods=['POST'])
def sign_stock_status():
    """Generate and sign Stock Status Report"""
    try:
        data = request.json
        signature_data = data.get('signature')
        signer_name = data.get('signer_name')
        
        if not signature_data or not signer_name:
            return jsonify({'error': 'Signature and signer name required'}), 400
        
        doc = StockStatusReportDocument()
        sample_data = get_sample_document_data('stock-status')
        pdf_bytes = doc.generate_pdf(sample_data)
        signed_pdf = add_signature_to_pdf(pdf_bytes, signature_data, signer_name)
        
        return send_file(
            BytesIO(signed_pdf),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'stock_status_signed_{datetime.now().strftime("%Y%m%d")}.pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@document_bp.route('/inventory/cycle-count/sign', methods=['POST'])
def sign_cycle_count():
    """Generate and sign Cycle Count Report"""
    try:
        data = request.json
        signature_data = data.get('signature')
        signer_name = data.get('signer_name')
        
        if not signature_data or not signer_name:
            return jsonify({'error': 'Signature and signer name required'}), 400
        
        doc = CycleCountReportDocument()
        sample_data = get_sample_document_data('cycle-count')
        pdf_bytes = doc.generate_pdf(sample_data)
        signed_pdf = add_signature_to_pdf(pdf_bytes, signature_data, signer_name)
        
        return send_file(
            BytesIO(signed_pdf),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'cycle_count_signed_{datetime.now().strftime("%Y%m%d")}.pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@document_bp.route('/fulfillment/pick-list/sign', methods=['POST'])
def sign_pick_list():
    """Generate and sign Pick List"""
    try:
        data = request.json
        signature_data = data.get('signature')
        signer_name = data.get('signer_name')
        
        if not signature_data or not signer_name:
            return jsonify({'error': 'Signature and signer name required'}), 400
        
        doc = PickListDocument()
        sample_data = get_sample_document_data('pick-list')
        pdf_bytes = doc.generate_pdf(sample_data)
        signed_pdf = add_signature_to_pdf(pdf_bytes, signature_data, signer_name)
        
        return send_file(
            BytesIO(signed_pdf),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'pick_list_signed_{datetime.now().strftime("%Y%m%d")}.pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@document_bp.route('/fulfillment/packing-slip/sign', methods=['POST'])
def sign_packing_slip():
    """Generate and sign Packing Slip"""
    try:
        data = request.json
        signature_data = data.get('signature')
        signer_name = data.get('signer_name')
        
        if not signature_data or not signer_name:
            return jsonify({'error': 'Signature and signer name required'}), 400
        
        doc = PackingSlipDocument()
        sample_data = get_sample_document_data('packing-slip')
        pdf_bytes = doc.generate_pdf(sample_data)
        signed_pdf = add_signature_to_pdf(pdf_bytes, signature_data, signer_name)
        
        return send_file(
            BytesIO(signed_pdf),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'packing_slip_signed_{datetime.now().strftime("%Y%m%d")}.pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@document_bp.route('/fulfillment/shipping-label/sign', methods=['POST'])
def sign_shipping_label():
    """Generate and sign Shipping Label"""
    try:
        data = request.json
        signature_data = data.get('signature')
        signer_name = data.get('signer_name')
        
        if not signature_data or not signer_name:
            return jsonify({'error': 'Signature and signer name required'}), 400
        
        doc = ShippingLabelDocument()
        sample_data = get_sample_document_data('shipping-label')
        pdf_bytes = doc.generate_pdf(sample_data)
        signed_pdf = add_signature_to_pdf(pdf_bytes, signature_data, signer_name)
        
        return send_file(
            BytesIO(signed_pdf),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'shipping_label_signed_{datetime.now().strftime("%Y%m%d")}.pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500
