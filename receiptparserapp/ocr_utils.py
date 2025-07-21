# ocr_utils.py (Universal File Processor)

from PIL import Image
from pdf2image import convert_from_bytes
from typing import IO, Union, List

def process_file(uploaded_file: IO) -> Union[Image.Image, str, None]:
    """
    Processes an uploaded file and returns either an Image object or a text string.
    """
    file_name = uploaded_file.name
    file_extension = file_name.split('.')[-1].lower()
    
    if file_extension in ['jpg', 'jpeg', 'png']:
        return Image.open(uploaded_file)
        
    elif file_extension == 'pdf':
        try:
            # Convert PDF to a list of images
            images = convert_from_bytes(uploaded_file.read())
            # Return the first page as an image for Vision AI processing
            if images:
                return images[0]
            return None # Handle empty PDFs
        except Exception as e:
            raise RuntimeError(f"Could not process PDF '{file_name}'. Ensure 'poppler' is installed. Error: {e}")

    elif file_extension == 'txt':
        # Read the text file and return its content as a string
        return uploaded_file.read().decode('utf-8')
        
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")