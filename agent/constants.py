from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv(override=True)

AUTH_DATA_DIR = Path(os.getenv("AUTH_DATA_DIR"))
GD_CREDENTIALS_FILE = Path(os.getenv("GD_CREDENTIALS_FILE"))

LLM_API_NAME = os.getenv("LLM_API_NAME")
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_API_BASE = os.getenv("LLM_API_BASE")