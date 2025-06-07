import json
from typing import Dict
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from interfaces import ExtractorInterface
from config.settings import AZURE_ENDPOINT, AZURE_MODEL, AZURE_TOKEN

class AzureExtractor(ExtractorInterface):
    
    def __init__(self):
        self.client = ChatCompletionsClient(
            endpoint=AZURE_ENDPOINT,
            credential=AzureKeyCredential(AZURE_TOKEN),
        )
    
    def extract_resume_info(self, text: str) -> Dict:
        prompt = f"""
        Extract the following from this resume:
        - Name
        - Email
        - Phone
        - Skills
        - Experience (in years)
        - Education
        - Summary

        Provide JSON with keys: name, email, phone, skills (list), experience_years, education, summary.

        Resume:
        {text}
        """
        try:
            response = self.client.complete(
                messages=[
                    SystemMessage("You are an expert resume parser."),
                    UserMessage(prompt),
                ],
                temperature=0.3,
                top_p=1,
                model=AZURE_MODEL
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            print(f"Azure extraction error: {str(e)}")
            return {}