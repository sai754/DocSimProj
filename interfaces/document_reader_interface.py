from abc import ABC, abstractmethod

class DocumentReaderInterface(ABC):
    
    @abstractmethod
    def read_document(self, file_path: str) -> str:
        pass
    
    @abstractmethod
    def read_pdf(self, file_path: str) -> str:
        pass
    
    @abstractmethod
    def read_docx(self, file_path: str) -> str:
        pass