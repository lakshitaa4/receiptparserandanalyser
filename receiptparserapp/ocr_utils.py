# ocr_utils.py (Final - No OpenCV)

import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
from typing import IO

def extract_text_from_file(file: IO) -> str:
    """
    Extracts raw text from a file using basic Tesseract, which works best for clean images.
    """
    file_extension = file.name.split('.')[-1].lower()
    
    if file_extension in ['jpg', 'jpeg', 'png']:
        image = Image.open(file)
        text = pytesseract.image_to_string(image)
        return text
        
    elif file_extension == 'pdf':
        try:
            images = convert_from_bytes(file.read())
            full_text = ""
            for img in images:
                # No pre-processing on PDF images either
                full_text += pytesseract.image_to_string(img) + "\n"
            return full_text
        except Exception as e:
            raise RuntimeError(f"Could not process PDF. Ensure 'poppler' is installed. Error: {e}")

    elif file_extension == 'txt':
        return file.read().decode('utf-8')
        
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")