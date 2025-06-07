from dataclasses import dataclass
from typing import List

@dataclass
class JobDescription:
    id: str
    title: str
    required_skills: List[str]
    experience_required: str
    raw_text: str
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "required_skills": self.required_skills,
            "experience_required": self.experience_required,
            "raw_text": self.raw_text
        }
    
    def __str__(self) -> str:
        return f"JobDescription(id={self.id}, title={self.title})"