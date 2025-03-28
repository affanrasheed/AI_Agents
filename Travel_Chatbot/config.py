"""
Configuration settings for the Travel Assistant application.
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY: Optional[str] = os.getenv("TAVILY_API_KEY")
LANGSMITH_API_KEY: Optional[str] = os.getenv("LANGSMITH_API_KEY")

# LangSmith configuration
LANGSMITH_TRACING: bool = os.getenv("LANGSMITH_TRACING", "true").lower() == "true"
LANGSMITH_ENDPOINT: str = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
LANGSMITH_PROJECT: str = os.getenv("LANGSMITH_PROJECT", "flight-chatbot")

# Database configuration
DB_URL: str = os.getenv(
    "DB_URL", "https://storage.googleapis.com/benchmarks-artifacts/travel-db/travel2.sqlite"
)
LOCAL_DB_PATH: str = os.getenv("LOCAL_DB_PATH", "travel2.sqlite")
BACKUP_DB_PATH: str = os.getenv("BACKUP_DB_PATH", "travel2.backup.sqlite")

# FAQ/Policy configuration
POLICY_URL: str = os.getenv(
    "POLICY_URL", "https://storage.googleapis.com/benchmarks-artifacts/travel-db/swiss_faq.md"
)

# LLM Configuration
LLM_MODEL: str = os.getenv("LLM_MODEL", "claude-3-5-haiku-latest")
LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "1.0"))

# UI Configuration
UI_TITLE: str = os.getenv("UI_TITLE", "Swiss Airlines Travel Assistant")
UI_SUBTITLE: str = os.getenv("UI_SUBTITLE", "Book flights, hotels, cars, and more")
UI_ICON: str = os.getenv("UI_ICON", "✈️")

# Default passenger ID for testing
DEFAULT_PASSENGER_ID: str = os.getenv("DEFAULT_PASSENGER_ID", "3442 587242")

# Initialize environment variables for LangSmith
if LANGSMITH_API_KEY:
    os.environ["LANGSMITH_API_KEY"] = LANGSMITH_API_KEY
    os.environ["LANGSMITH_TRACING"] = str(LANGSMITH_TRACING).lower()
    os.environ["LANGSMITH_ENDPOINT"] = LANGSMITH_ENDPOINT
    os.environ["LANGSMITH_PROJECT"] = LANGSMITH_PROJECT