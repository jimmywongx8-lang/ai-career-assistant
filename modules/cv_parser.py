# cv_parser.py
import fitz  # PyMuPDF
import docx
import os

def extract_text_from_file(file_path):
    """Extract clean text from PDF or DOCX"""
    if not os.path.exists(file_path):
        return None
    
    text = ""
    try:
        if file_path.lower().endswith('.pdf'):
            doc = fitz.open(file_path)
            for page in doc:
                text += page.get_text()
            doc.close()
        elif file_path.lower().endswith('.docx'):
            doc = docx.Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
        
        # Clean up extra whitespace
        return " ".join(text.split())
    except Exception as e:
        print(f"Error parsing file: {e}")
        return None