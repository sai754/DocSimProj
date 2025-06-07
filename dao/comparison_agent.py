from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from interfaces import ComparisonInterface
from entities import Profile, JobDescription
from config.settings import MAX_TFIDF_FEATURES, NGRAM_RANGE

class ComparisonAgent(ComparisonInterface):
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            stop_words='english', 
            max_features=MAX_TFIDF_FEATURES, 
            ngram_range=NGRAM_RANGE
        )

    def calculate_similarity(self, job_description: JobDescription, profile: Profile) -> float:
        documents = [job_description.raw_text, profile.raw_text]
        tfidf_matrix = self.vectorizer.fit_transform(documents)
        text_similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

        jd_skills = set(s.lower() for s in job_description.required_skills)
        profile_skills = set(s.lower() for s in profile.skills)
        skill_similarity = len(jd_skills & profile_skills) / len(jd_skills) if jd_skills else 0

        title_similarity = 1.0 if job_description.title.lower() in profile.raw_text.lower() else 0.0

        return 0.6 * text_similarity + 0.3 * skill_similarity + 0.1 * title_similarity

    def compare_profiles_with_jd(self, job_description: JobDescription, profiles: List[Profile]) -> List[Profile]:
        for profile in profiles:
            profile.similarity_score = self.calculate_similarity(job_description, profile)
        return profiles