from dataclasses import dataclass
from typing import List

@dataclass
class Profile:
    id: str
    name: str
    email: str
    phone: str
    skills: List[str]
    experience: str
    education: str
    summary: str
    raw_text: str
    similarity_score: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "skills": self.skills,
            "experience": self.experience,
            "education": self.education,
            "summary": self.summary,
            "similarity_score": self.similarity_score
        }
    
    def __str__(self) -> str:
        return f"Profile(name={self.name}, score={self.similarity_score:.2f})"