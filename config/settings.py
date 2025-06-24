import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def get_env_var(key: str, default: str = None) -> str:
    """
    Get environment variable with fallback to Streamlit secrets
    Priority: Environment Variables -> Streamlit Secrets -> Default
    """
    # First try environment variables
    env_value = os.getenv(key)
    if env_value:
        return env_value
    
    # Then try Streamlit secrets (only if streamlit is available and secrets exist)
    try:
        if hasattr(st, 'secrets') and st.secrets:
            return st.secrets.get(key, default)
    except Exception:
        # If secrets are not available or there's an error, fall back to default
        pass
    
    return default

# Azure AI Configuration
AZURE_ENDPOINT = "https://models.github.ai/inference"
AZURE_MODEL = "openai/gpt-4.1-mini"
AZURE_TOKEN = get_env_var("AZURE_OPEN_API")

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = get_env_var("EMAIL_ADDRESS")
EMAIL_PASSWORD = get_env_var("EMAIL_PASSWORD")

# Matching Configuration
MIN_SIMILARITY_THRESHOLD = 0.3
DEFAULT_TOP_MATCHES = 3
MAX_TFIDF_FEATURES = 1000
NGRAM_RANGE = (1, 2)

# File Paths
RESUME_FOLDER = "data/resumes"
OUTPUT_FOLDER = "data/outputs"
DEFAULT_CSV_FILENAME = "ranked_candidates.csv"

# Validation function to check if required environment variables are set
def validate_config():
    """Validate that required configuration is available"""
    missing_vars = []
    
    if not AZURE_TOKEN:
        missing_vars.append("AZURE_OPEN_API")
    
    if not EMAIL_ADDRESS:
        missing_vars.append("EMAIL_ADDRESS")
    
    if not EMAIL_PASSWORD:
        missing_vars.append("EMAIL_PASSWORD")
    
    return missing_vars