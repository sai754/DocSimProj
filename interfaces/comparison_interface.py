from abc import ABC, abstractmethod
from typing import List
from entities import Profile, JobDescription

class ComparisonInterface(ABC):
    
    @abstractmethod
    def calculate_similarity(self, job_description: JobDescription, profile: Profile) -> float:
        pass
    
    @abstractmethod
    def compare_profiles_with_jd(self, job_description: JobDescription, profiles: List[Profile]) -> List[Profile]:
        pass