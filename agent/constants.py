import logging
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

_log_level = os.getenv("LOG_LEVEL", "INFO")

match _log_level:
    case "NOTSET":
        LOG_LEVEL = logging.NOTSET
    case "DEBUG":
        LOG_LEVEL = logging.DEBUG
    case "INFO":
        LOG_LEVEL = logging.INFO
    case "WARNING":
        LOG_LEVEL = logging.WARNING
    case "ERROR":
        LOG_LEVEL = logging.ERROR
    case "CRITICAL":
        LOG_LEVEL = logging.CRITICAL
    case _:
        LOG_LEVEL = logging.INFO

