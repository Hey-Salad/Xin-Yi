#!/usr/bin/env python3
"""Test document generation"""

import sys
import os
sys.path.insert(0, 'backend')

from services.inventory_documents import StockStatusReportDocument
from datetime import datetime

# Test data
data = {
    'report_date': datetime.now(),
    'company_name': 'HeySalad - Xin Yi WMS',
    'items': [
        {
            'sku': 'TEST001',
            'name': 'Test Product',
            'quantity': 100,
            'safe_stock': 50,
            'reorder_point': 50,
            'status': 'normal'
        }
    ]
}

try:
    print("🔧 Testing Stock Status Report generation...")
    doc_generator = StockStatusReportDocument(company_name=data['company_name'])
    pdf_bytes = doc_generator.generate_pdf(data)
    
    # Save to file
    with open('/tmp/test_stock_status.pdf', 'wb') as f:
        f.write(pdf_bytes)
    
    print(f"✅ Success! Generated {len(pdf_bytes)} bytes")
    print("📄 Saved to /tmp/test_stock_status.pdf")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
