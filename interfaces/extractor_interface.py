from abc import ABC, abstractmethod
from typing import Dict

class ExtractorInterface(ABC):
    
    @abstractmethod
    def extract_resume_info(self, text: str) -> Dict:
        pass