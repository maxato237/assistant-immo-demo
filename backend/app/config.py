import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / ".env")


class Config:
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
    LLM_MODEL = os.getenv("LLM_MODEL", "ministral-14b-latest")
    EMBED_MODEL = os.getenv("EMBED_MODEL", "mistral-embed")

    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:4200")
    RATE_LIMIT_ASK = os.getenv("RATE_LIMIT_ASK", "20 per hour;5 per minute")
    DAILY_QUOTA = int(os.getenv("DAILY_QUOTA", "300"))

    TOP_K = 6
    MAX_ANSWER_TOKENS = 400

    DOCUMENTS_DIR = BACKEND_DIR / "data" / "documents"
    INDEX_DIR = BACKEND_DIR / "data" / "index"
    SYSTEM_PROMPT_FILE = BACKEND_DIR / "app" / "prompts" / "system_prompt.txt"
