# Xin Yi WMS - Document Generation System

## Overview

A comprehensive document generation system for warehouse management operations, inspired by the invoice system from heysalad-cash. This system generates professional PDF documents for all warehouse operations.

## Architecture

**Technology Stack:**
- **PDF Generation**: ReportLab (Python equivalent of pdfkit)
- **Barcodes/QR Codes**: python-barcode, qrcode, pillow
- **Backend**: Flask REST API
- **Storage**: Can integrate with Supabase Storage (like heysalad-cash)

**Components:**
- `backend/services/document_service.py` - Base document generator class
- `backend/services/receiving_documents.py` - Receiving operation documents
- `backend/services/inventory_documents.py` - Inventory management documents
- `backend/services/fulfillment_documents.py` - Order fulfillment & shipping documents
- `backend/routes/document_routes.py` - REST API endpoints

---

## Available Documents

### 1. Receiving Documents

#### A. Purchase Order (PO) Receipt
**Endpoint:** `POST /api/documents/receiving/po-receipt`

Confirms receipt of goods from a vendor.

**Request Body:**
```json
{
  "po_number": "PO-2024-001",
  "vendor": "ABC Supplies Inc.",
  "received_date": "2024-11-19T10:30:00",
  "receiver": "John Doe",
  "items": [
    {
      "sku": "SKU-001",
      "name": "Product Name",
      "ordered_qty": 100,
      "received_qty": 100,
      "lot_number": "LOT-001",
      "expiration_date": "2025-06-30",
      "condition": "Good"
    }
  ],
  "notes": "All items received in good condition"
}
```

**Features:**
- Item details with ordered vs received quantities
- Lot number and expiration date tracking
- Condition reporting
- Signature section

---

#### B. Receiving Report
**Endpoint:** `POST /api/documents/receiving/receiving-report`

Summary of all receipts for a time period.

**Request Body:**
```json
{
  "report_date": "2024-11-19T00:00:00",
  "period": "Daily",
  "receipts": [
    {
      "po_number": "PO-2024-001",
      "vendor": "ABC Supplies",
      "items_count": 5,
      "total_quantity": 250,
      "received_time": "2024-11-19T10:30:00"
    }
  ],
  "summary": {
    "total_receipts": 10,
    "total_items": 45,
    "total_quantity": 1500
  }
}
```

---

#### C. Putaway Report
**Endpoint:** `POST /api/documents/receiving/putaway-report`

Tracks where received items were stored in the warehouse.

**Request Body:**
```json
{
  "report_id": "PUT-2024-001",
  "date": "2024-11-19T14:00:00",
  "operator": "Jane Smith",
  "items": [
    {
      "sku": "SKU-001",
      "name": "Product Name",
      "lot_number": "LOT-001",
      "quantity": 100,
      "from_location": "Receiving",
      "to_location": "A-01-02",
      "status": "Completed"
    }
  ]
}
```

---

### 2. Inventory Documents

#### A. Inventory Report
**Endpoint:** `POST /api/documents/inventory/inventory-report` or `GET /api/documents/inventory/inventory-report`

Complete inventory snapshot.

**Auto-generate from database (GET):**
```bash
curl -X GET http://localhost:2124/api/documents/inventory/inventory-report
```

**Or provide custom data (POST):**
```json
{
  "report_date": "2024-11-19T00:00:00",
  "warehouse": "Main Warehouse",
  "items": [
    {
      "sku": "SKU-001",
      "name": "Product Name",
      "category": "Food",
      "quantity": 500,
      "unit": "kg",
      "location": "A-01-02",
      "value": 5000.00
    }
  ],
  "summary": {
    "total_items": 150,
    "total_quantity": 10000,
    "total_value": 150000.00
  }
}
```

---

#### B. Stock Status Report
**Endpoint:** `POST /api/documents/inventory/stock-status` or `GET /api/documents/inventory/stock-status`

Focuses on stock levels and alerts.

**Auto-generate from database (GET):**
```bash
curl -X GET http://localhost:2124/api/documents/inventory/stock-status
```

**Features:**
- Color-coded status indicators (normal/low/critical)
- Safe stock comparisons
- Reorder point tracking

---

#### C. Cycle Count Report
**Endpoint:** `POST /api/documents/inventory/cycle-count`

Physical count verification vs system records.

**Request Body:**
```json
{
  "count_id": "CC-2024-001",
  "count_date": "2024-11-19T16:00:00",
  "counter": "Mike Johnson",
  "location": "Zone A",
  "items": [
    {
      "sku": "SKU-001",
      "name": "Product Name",
      "system_qty": 500,
      "counted_qty": 498,
      "variance": -2,
      "location": "A-01-02"
    }
  ],
  "summary": {
    "items_counted": 50,
    "variances_found": 5,
    "accuracy_rate": 90.0
  }
}
```

**Features:**
- Variance highlighting (red for discrepancies)
- Accuracy rate calculation
- Location-specific counts

---

### 3. Order Fulfillment & Shipping Documents

#### A. Pick List
**Endpoint:** `POST /api/documents/fulfillment/pick-list`

Instructions for warehouse picking.

**Request Body:**
```json
{
  "order_number": "ORD-2024-001",
  "pick_date": "2024-11-19T09:00:00",
  "picker": "John Doe",
  "priority": "High",
  "items": [
    {
      "sku": "SKU-001",
      "name": "Product Name",
      "quantity": 20,
      "location": "A-01-02",
      "lot_number": "LOT-001"
    }
  ],
  "notes": "Handle with care - fragile items"
}
```

**Features:**
- Checkboxes for each item
- Location guidance (optimized route)
- Lot number specification (for FEFO)
- Space to record picked quantities
- Signature section

---

#### B. Packing Slip
**Endpoint:** `POST /api/documents/fulfillment/packing-slip`

Contents of a shipment for the customer.

**Request Body:**
```json
{
  "order_number": "ORD-2024-001",
  "packing_date": "2024-11-19T10:00:00",
  "ship_to": {
    "name": "ABC Restaurant",
    "address_line1": "123 Main St",
    "address_line2": "Suite 100",
    "city": "New York",
    "state": "NY",
    "postal_code": "10001",
    "country": "USA"
  },
  "items": [
    {
      "sku": "SKU-001",
      "name": "Product Name",
      "quantity": 20,
      "lot_number": "LOT-001"
    }
  ],
  "tracking_number": "1Z999AA10123456784",
  "carrier": "UPS"
}
```

---

#### C. Shipping Label
**Endpoint:** `POST /api/documents/fulfillment/shipping-label`

Address label for packages (4x6 inch format).

**Request Body:**
```json
{
  "tracking_number": "1Z999AA10123456784",
  "carrier": "UPS",
  "service_level": "Ground",
  "ship_date": "2024-11-19T10:00:00",
  "from_address": {
    "name": "Xin Yi Warehouse",
    "address_line1": "456 Warehouse Dr",
    "city": "Los Angeles",
    "state": "CA",
    "postal_code": "90001"
  },
  "to_address": {
    "name": "ABC Restaurant",
    "address_line1": "123 Main St",
    "city": "New York",
    "state": "NY",
    "postal_code": "10001",
    "country": "USA"
  },
  "weight": 25.5,
  "dimensions": "12x10x8"
}
```

**Features:**
- Barcode for tracking number
- Large, clear TO address
- Compact FROM address
- Weight and dimensions

---

#### D. Bill of Lading (BOL)
**Endpoint:** `POST /api/documents/shipping/bill-of-lading`

Freight shipping documentation.

**Request Body:**
```json
{
  "bol_number": "BOL-2024-001",
  "shipment_date": "2024-11-19T10:00:00",
  "carrier": "XYZ Freight",
  "pro_number": "PRO-123456",
  "shipper": {
    "name": "Xin Yi Warehouse",
    "address_line1": "456 Warehouse Dr",
    "city": "Los Angeles",
    "state": "CA",
    "postal_code": "90001"
  },
  "consignee": {
    "name": "ABC Restaurant",
    "address_line1": "123 Main St",
    "city": "New York",
    "state": "NY",
    "postal_code": "10001"
  },
  "items": [
    {
      "description": "Frozen Food Products",
      "quantity": 50,
      "weight": 1250.0,
      "class": "55"
    }
  ],
  "special_instructions": "Keep refrigerated. Temperature control required."
}
```

---

## Installation

### 1. Install Dependencies

```bash
# Navigate to project root
cd /home/admin/Xin-Yi

# Install using uv (recommended)
uv pip install -e .

# Or using pip
pip install -e .
```

This will install:
- `reportlab>=4.0.0` - PDF generation
- `qrcode>=7.4.2` - QR code generation
- `pillow>=10.0.0` - Image processing
- `python-barcode>=0.15.0` - Barcode generation

### 2. Verify Installation

```bash
# Start the backend server
cd backend
python app_platform.py
```

You should see:
```
📦 Available Services:
  • WMS (Xin Yi): /api/wms/*
  • Documents: /api/documents/*
  • AI Services: /api/ai/*
  ...
```

---

## Usage Examples

### Example 1: Generate Inventory Report from Database

```bash
curl -X GET http://localhost:2124/api/documents/inventory/inventory-report \
  --output inventory_report.pdf
```

This automatically pulls all materials from your Supabase database and generates a complete inventory report.

### Example 2: Generate Pick List

```bash
curl -X POST http://localhost:2124/api/documents/fulfillment/pick-list \
  -H "Content-Type: application/json" \
  -d '{
    "order_number": "ORD-2024-001",
    "pick_date": "2024-11-19T09:00:00",
    "picker": "John Doe",
    "items": [
      {
        "sku": "LONGDAN-001",
        "name": "Premium Soy Sauce",
        "quantity": 10,
        "location": "A-01-02"
      }
    ]
  }' \
  --output pick_list.pdf
```

### Example 3: Generate PO Receipt

```bash
curl -X POST http://localhost:2124/api/documents/receiving/po-receipt \
  -H "Content-Type: application/json" \
  -d @po_receipt_data.json \
  --output po_receipt.pdf
```

Where `po_receipt_data.json`:
```json
{
  "po_number": "PO-2024-001",
  "vendor": "Longdan Foods",
  "received_date": "2024-11-19T10:30:00",
  "receiver": "Warehouse Staff",
  "items": [
    {
      "sku": "LONGDAN-001",
      "name": "Premium Soy Sauce 500ml",
      "ordered_qty": 100,
      "received_qty": 100,
      "lot_number": "LOT-20241119",
      "expiration_date": "2025-11-18",
      "condition": "Good"
    }
  ]
}
```

---

## API Reference

### Get Available Documents

**Endpoint:** `GET /api/documents/available`

Returns a list of all available document types with descriptions.

**Response:**
```json
{
  "receiving": [...],
  "inventory": [...],
  "fulfillment": [...]
}
```

---

## Customization

### Custom Company Branding

All document generators accept optional company information:

```python
{
  "company_name": "Your Company Name",
  "company_info": {
    "address": "123 Business St, City, ST 12345",
    "phone": "+1-555-0123",
    "email": "info@yourcompany.com"
  },
  ...
}
```

### Adding Custom Document Types

1. Create a new document class in the appropriate service file
2. Inherit from `DocumentGenerator`
3. Implement the `generate_pdf()` method
4. Add a route in `document_routes.py`

Example:
```python
class CustomDocument(DocumentGenerator):
    def generate_pdf(self, data: Dict[str, Any]) -> bytes:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # Add your custom content
        elements.extend(self._create_header())
        # ...

        doc.build(elements, onFirstPage=self._create_footer)
        buffer.seek(0)
        return buffer.getvalue()
```

---

## Integration with Frontend

### JavaScript Example

```javascript
async function generatePickList(orderData) {
  const response = await fetch('http://localhost:2124/api/documents/fulfillment/pick-list', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(orderData)
  });

  if (response.ok) {
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `pick_list_${orderData.order_number}.pdf`;
    a.click();
  }
}
```

---

## Features Comparison with heysalad-cash

| Feature | heysalad-cash (Invoice) | Xin Yi WMS (Documents) |
|---------|-------------------------|------------------------|
| **Technology** | TypeScript/pdfkit | Python/ReportLab |
| **Document Types** | Invoices | 10+ WMS documents |
| **QR Codes** | ✓ (Crypto wallets) | ✓ (Tracking) |
| **Barcodes** | ✗ | ✓ (Shipping labels) |
| **Tables** | ✓ (Line items) | ✓ (All documents) |
| **Professional Layout** | ✓ | ✓ |
| **Signature Sections** | ✗ | ✓ |
| **Auto-generation** | Manual | ✓ (Inventory/Stock) |

---

## Document Storage (Future Enhancement)

Similar to heysalad-cash invoice storage, you can integrate Supabase Storage:

```python
from database_supabase import get_supabase_client

def save_document_to_storage(pdf_bytes: bytes, filename: str):
    supabase = get_supabase_client()

    # Upload to Supabase Storage
    supabase.storage.from_('wms-documents').upload(
        f'documents/{filename}',
        pdf_bytes,
        file_options={"content-type": "application/pdf"}
    )

    # Get signed URL
    url = supabase.storage.from_('wms-documents').create_signed_url(
        f'documents/{filename}',
        3600  # 1 hour expiry
    )

    return url
```

---

## Troubleshooting

### Issue: PDF generation fails

**Solution:** Ensure all dependencies are installed:
```bash
uv pip install reportlab qrcode pillow python-barcode
```

### Issue: Barcode doesn't appear

**Solution:** The barcode library requires valid codes. For tracking numbers, use:
- UPS: 18 characters starting with "1Z"
- FedEx: 12 or 15 digits
- Code128: Any alphanumeric string

### Issue: Import errors

**Solution:** Make sure the `backend/services/__init__.py` file exists.

---

## Future Enhancements

1. **Email Delivery** - Send documents via SendGrid (like heysalad-cash invoices)
2. **Document Templates** - Customizable PDF templates
3. **Batch Generation** - Generate multiple documents at once
4. **Document Archive** - Store in Supabase with metadata
5. **Digital Signatures** - Add cryptographic signatures
6. **Internationalization** - Multi-language support
7. **Document Tracking** - Track who generated/viewed documents
8. **Auto-generation** - Trigger document creation on WMS events

---

## API Summary

| Document Type | HTTP Method | Endpoint |
|--------------|-------------|----------|
| PO Receipt | POST | `/api/documents/receiving/po-receipt` |
| Receiving Report | POST | `/api/documents/receiving/receiving-report` |
| Putaway Report | POST | `/api/documents/receiving/putaway-report` |
| Inventory Report | GET/POST | `/api/documents/inventory/inventory-report` |
| Stock Status | GET/POST | `/api/documents/inventory/stock-status` |
| Cycle Count | POST | `/api/documents/inventory/cycle-count` |
| Pick List | POST | `/api/documents/fulfillment/pick-list` |
| Packing Slip | POST | `/api/documents/fulfillment/packing-slip` |
| Shipping Label | POST | `/api/documents/fulfillment/shipping-label` |
| Bill of Lading | POST | `/api/documents/shipping/bill-of-lading` |

---

## License

Part of the Xin Yi WMS - HeySalad Platform
© 2024 HeySalad OÜ

---

**Ready to use!** 🚀

Generate your first document:
```bash
curl -X GET http://localhost:2124/api/documents/inventory/inventory-report --output test.pdf && open test.pdf
```
