import os
from dotenv import load_dotenv

load_dotenv()

AZURE_ENDPOINT = "https://models.github.ai/inference"
AZURE_MODEL = "openai/gpt-4.1-mini"
AZURE_TOKEN = os.getenv("AZURE_OPEN_API")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

MIN_SIMILARITY_THRESHOLD = 0.3
DEFAULT_TOP_MATCHES = 3
MAX_TFIDF_FEATURES = 1000
NGRAM_RANGE = (1, 2)

RESUME_FOLDER = "data/resumes"
OUTPUT_FOLDER = "data/outputs"
DEFAULT_CSV_FILENAME = "ranked_candidates.csv"