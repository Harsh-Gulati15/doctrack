import os
import re
import pytesseract
from PIL import Image
from flask import current_app


def extract_text(file_path, file_type):
    """Extract text from PDF or image using Tesseract OCR.
    
    Args:
        file_path: Absolute path to the uploaded file
        file_type: 'pdf', 'jpeg', or 'png'
    
    Returns:
        Cleaned text string, or None on failure
    """
    try:
        tesseract_path = current_app.config.get(
            'TESSERACT_PATH', r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        )
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        text_parts = []
        
        if file_type == 'pdf':
            from pdf2image import convert_from_path
            poppler_path = current_app.config.get('POPPLER_PATH')
            images = convert_from_path(
                file_path,
                dpi=300,
                poppler_path=poppler_path if poppler_path else None
            )
            for page_img in images:
                page_text = pytesseract.image_to_string(page_img)
                text_parts.append(page_text)
        else:  # jpeg or png
            img = Image.open(file_path)
            page_text = pytesseract.image_to_string(img)
            text_parts.append(page_text)
        
        # Concatenate and clean
        full_text = '\n'.join(text_parts)
        full_text = full_text.replace('\x00', '')  # Remove null chars
        full_text = re.sub(r'[ \t]+', ' ', full_text)  # Collapse horizontal whitespace
        full_text = re.sub(r'\n{3,}', '\n\n', full_text)  # Max 2 newlines
        full_text = full_text.strip()
        
        return full_text if full_text else None
        
    except Exception as e:
        current_app.logger.error(f'OCR extraction failed: {e}')
        return None
