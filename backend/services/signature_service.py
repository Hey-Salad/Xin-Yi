"""
Signature Service for adding signatures to PDF documents
"""

try:
    from PyPDF2 import PdfReader, PdfWriter
except ImportError:
    from pypdf import PdfReader, PdfWriter

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image
import io
import base64
import os
import tempfile
from datetime import datetime


def add_signature_to_pdf(pdf_bytes, signature_data, signer_name):
    """
    Add a signature image to the bottom of a PDF document
    
    Args:
        pdf_bytes: Original PDF as bytes
        signature_data: Base64 encoded signature image (data:image/png;base64,...)
        signer_name: Name of the person signing
        
    Returns:
        bytes: PDF with signature added
    """
    try:
        # Decode signature image from base64
        if ',' in signature_data:
            signature_data = signature_data.split(',')[1]
        
        signature_bytes = base64.b64decode(signature_data)
        signature_img = Image.open(io.BytesIO(signature_bytes))
        
        # Save signature to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        temp_sig_path = temp_file.name
        temp_file.close()
        signature_img.save(temp_sig_path, 'PNG')
        
        # Read original PDF
        pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
        pdf_writer = PdfWriter()
        
        # Create signature overlay
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        
        # Position signature at bottom right
        page_width, page_height = letter
        sig_width = 150
        sig_height = 50
        sig_x = page_width - sig_width - 50  # 50 points from right edge
        sig_y = 80  # 80 points from bottom
        
        # Draw signature image
        can.drawImage(temp_sig_path, sig_x, sig_y, width=sig_width, height=sig_height, 
                     preserveAspectRatio=True, mask='auto')
        
        # Add signer name and timestamp below signature
        can.setFont('Helvetica', 8)
        can.drawString(sig_x, sig_y - 15, f"Signed by: {signer_name}")
        can.drawString(sig_x, sig_y - 28, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        can.save()
        
        # Move to the beginning of the StringIO buffer
        packet.seek(0)
        overlay_pdf = PdfReader(packet)
        
        # Add signature overlay to last page
        for i, page in enumerate(pdf_reader.pages):
            if i == len(pdf_reader.pages) - 1:  # Last page
                page.merge_page(overlay_pdf.pages[0])
            pdf_writer.add_page(page)
        
        # Write to output
        output = io.BytesIO()
        pdf_writer.write(output)
        output.seek(0)
        
        # Clean up temp file
        if os.path.exists(temp_sig_path):
            os.remove(temp_sig_path)
        
        return output.getvalue()
        
    except Exception as e:
        import traceback
        print(f"Error adding signature to PDF: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise Exception(f"Failed to add signature: {str(e)}")
