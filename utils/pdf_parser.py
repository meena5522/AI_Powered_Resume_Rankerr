import os
import logging
from PyPDF2 import PdfReader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts text content from a PDF file using PyPDF2.
    
    Args:
        file_path (str): The absolute path to the PDF file.
        
    Returns:
        str: Extracted text contents.
        
    Raises:
        ValueError: If file is invalid, encrypted, or cannot be read.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        raise FileNotFoundError(f"Resume file not found at {file_path}")
        
    text_content = []
    try:
        reader = PdfReader(file_path)
        
        # Check if the PDF is encrypted
        if reader.is_encrypted:
            logger.warning(f"Encrypted PDF encountered: {file_path}")
            # Try to decrypt with empty password
            try:
                reader.decrypt("")
            except Exception:
                raise ValueError("The uploaded PDF is encrypted and password-protected. Please upload an unencrypted file.")
                
        # Iterate and extract text page by page
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text_content.append(page_text)
                
    except Exception as e:
        logger.exception(f"Error parsing PDF file {file_path}: {e}")
        raise ValueError(f"Failed to read or parse PDF file: {str(e)}")
        
    full_text = "\n".join(text_content).strip()
    
    if not full_text:
        logger.warning(f"No readable text extracted from PDF: {file_path}")
        raise ValueError("The uploaded PDF does not contain any readable text. It might be scanned/image-only. Please upload a PDF with select-able text.")
        
    return full_text
