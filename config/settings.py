import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def get_env_var(key: str, default: str = None) -> str:
    try:
        return st.secrets[key]
    except (KeyError, AttributeError):
        return os.getenv(key, default)

AZURE_ENDPOINT = "https://models.github.ai/inference"
AZURE_MODEL = "openai/gpt-4.1-mini"
AZURE_TOKEN = get_env_var("AZURE_OPEN_API")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = get_env_var("EMAIL_ADDRESS")
EMAIL_PASSWORD = get_env_var("EMAIL_PASSWORD")

MIN_SIMILARITY_THRESHOLD = 0.3
DEFAULT_TOP_MATCHES = 3
MAX_TFIDF_FEATURES = 1000
NGRAM_RANGE = (1, 2)

RESUME_FOLDER = "data/resumes"
OUTPUT_FOLDER = "data/outputs"
DEFAULT_CSV_FILENAME = "ranked_candidates.csv"