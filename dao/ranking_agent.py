from typing import List
from interfaces import RankingInterface
from entities import Profile
from config.settings import MIN_SIMILARITY_THRESHOLD, DEFAULT_TOP_MATCHES
import json
import re
import os
from typing import List

from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential


AZURE_ENDPOINT = "https://models.github.ai/inference"
AZURE_MODEL = "openai/gpt-4.1-mini"
AZURE_TOKEN = os.getenv("AZURE_OPEN_API")

client = ChatCompletionsClient(
    endpoint=AZURE_ENDPOINT,
    credential=AzureKeyCredential(AZURE_TOKEN),
)

class RankingAgent(RankingInterface):
    def __init__(self, min_similarity_threshold: float = MIN_SIMILARITY_THRESHOLD):
        self.min_similarity_threshold = min_similarity_threshold

    def rank_profiles(self, profiles: List[Profile]) -> List[Profile]:
        qualified = [p for p in profiles if p.similarity_score >= self.min_similarity_threshold]

        if not qualified:
            return []

        ranking_prompt = f"""
You are an expert recruiter. Given a list of candidate profiles with similarity scores, rank them from best to worst based on how well they match a job. Consider skills, experience, and education to decide the final order.

Input Profiles:
{json.dumps([
    {
        "id": p.id,
        "name": p.name,
        "similarity_score": p.similarity_score,
        "summary": p.summary,
        "skills": p.skills,
        "experience": p.experience,
        "education": p.education
    } for p in qualified
], indent=2)}

Return a JSON array sorted by best match, with: id, name, similarity_score.
"""

        try:
            response = client.complete(
                messages=[
                    SystemMessage("You are a resume ranking expert."),
                    UserMessage(ranking_prompt)
                ],
                temperature=0.2,
                model=AZURE_MODEL
            )
            content = response.choices[0].message.content
            print("Azure final ranking response:", content)
            
            if content.strip().startswith("```"):
                import re
                content = re.sub(r"```(?:json)?\n?(.*?)```", r"\1", content.strip(), flags=re.DOTALL)

            ranked_data = json.loads(content)
            id_order = [item['id'] for item in ranked_data]
            id_map = {p.id: p for p in qualified}
            return [id_map[i] for i in id_order if i in id_map]

        except Exception as e:
            print("Azure ranking error (fallback to local sort):", e)
            return sorted(qualified, key=lambda x: x.similarity_score, reverse=True)

    def get_top_matches(self, profiles: List[Profile], top_n: int = DEFAULT_TOP_MATCHES) -> List[Profile]:
        return self.rank_profiles(profiles)[:top_n]
