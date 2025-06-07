from abc import ABC, abstractmethod
from typing import List
from entities import Profile

class RankingInterface(ABC):
    
    @abstractmethod
    def rank_profiles(self, profiles: List[Profile]) -> List[Profile]:
        pass
    
    @abstractmethod
    def get_top_matches(self, profiles: List[Profile], top_n: int) -> List[Profile]:
        pass