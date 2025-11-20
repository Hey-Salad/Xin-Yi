#!/usr/bin/env python3
"""
Quick test script for WMS document generation
"""

import sys
sys.path.insert(0, 'backend')

from datetime import datetime
from services.inventory_documents import StockStatusReportDocument

# Test data
test_data = {
    'report_date': datetime.now(),
    'items': [
        {
            'sku': 'LONGDAN-001',
            'name': 'Premium Soy Sauce 500ml',
            'quantity': 150,
            'safe_stock': 100,
            'reorder_point': 100,
            'status': 'normal'
        },
        {
            'sku': 'LONGDAN-002',
            'name': 'Rice Vinegar 1L',
            'quantity': 45,
            'safe_stock': 50,
            'reorder_point': 50,
            'status': 'low'
        },
        {
            'sku': 'LONGDAN-003',
            'name': 'Sesame Oil 250ml',
            'quantity': 15,
            'safe_stock': 50,
            'reorder_point': 50,
            'status': 'critical'
        }
    ]
}

# Generate document
print("🔧 Testing Stock Status Report generation...")
doc_generator = StockStatusReportDocument(company_name='Xin Yi WMS - Test')
pdf_bytes = doc_generator.generate_pdf(test_data)

# Save to file
output_file = 'test_stock_status.pdf'
with open(output_file, 'wb') as f:
    f.write(pdf_bytes)

print(f"✅ Document generated successfully!")
print(f"📄 Saved to: {output_file}")
print(f"📊 File size: {len(pdf_bytes):,} bytes")
print(f"\n✨ Open the PDF to verify it looks correct!")
