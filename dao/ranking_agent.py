from typing import List
from interfaces import RankingInterface
from entities import Profile
from config.settings import MIN_SIMILARITY_THRESHOLD, DEFAULT_TOP_MATCHES

class RankingAgent(RankingInterface):
    
    def __init__(self, min_similarity_threshold: float = MIN_SIMILARITY_THRESHOLD):
        self.min_similarity_threshold = min_similarity_threshold

    def rank_profiles(self, profiles: List[Profile]) -> List[Profile]:
        qualified = [p for p in profiles if p.similarity_score >= self.min_similarity_threshold]
        return sorted(qualified, key=lambda x: x.similarity_score, reverse=True)

    def get_top_matches(self, profiles: List[Profile], top_n: int = DEFAULT_TOP_MATCHES) -> List[Profile]:
        return self.rank_profiles(profiles)[:top_n]