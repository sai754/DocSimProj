from abc import ABC, abstractmethod
from typing import Dict

class CommunicationInterface(ABC):
    
    @abstractmethod
    def send_email(self, recipient_email: str, subject: str, body: str) -> None:
        pass
    
    @abstractmethod
    def notify(self, match_result: Dict) -> None:
        pass