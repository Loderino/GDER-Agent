import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)

AUTH_DATA_DIR = Path(os.getenv("AUTH_DATA_DIR"))
CACHE_DIR = Path(os.getenv("CACHE_DIR"))
GD_CREDENTIALS_FILE = Path(os.getenv("GD_CREDENTIALS_FILE"))

LLM_API_NAME = os.getenv("LLM_API_NAME", "gpt-4o-2024-11-20")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL")
