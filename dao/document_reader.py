import pdfplumber
import fitz
from docx import Document
from pathlib import Path
import warnings
from interfaces import DocumentReaderInterface

warnings.filterwarnings("ignore", message="CropBox missing from /Page, defaulting to MediaBox")

class DocumentReader(DocumentReaderInterface):
    
    def read_pdf(self, file_path: str) -> str:
        try:
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text.strip()
        except Exception:
            try:
                doc = fitz.open(file_path)
                return "\n".join([page.get_text() for page in doc]).strip()
            except Exception:
                return ""

    def read_docx(self, file_path: str) -> str:
        try:
            doc = Document(file_path)
            return "\n".join(p.text for p in doc.paragraphs).strip()
        except Exception:
            return ""

    def read_document(self, file_path: str) -> str:
        ext = Path(file_path).suffix.lower()
        if ext == '.pdf':
            return self.read_pdf(file_path)
        elif ext == '.docx':
            return self.read_docx(file_path)
        return ""