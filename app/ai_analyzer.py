import pdfplumber
from fastapi import UploadFile

def extract_text_from_pdf(file: UploadFile) -> str:
    """
    Extrahiert Text aus einer PDF-Datei
    """
    text = ""
    
    try:
        with pdfplumber.open(file.file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        return text.strip()
    
    except Exception as e:
        raise Exception(f"Fehler beim Lesen der PDF: {str(e)}")
