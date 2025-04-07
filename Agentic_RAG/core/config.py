import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# LangSmith Configuration
LANGSMITH_TRACING = os.environ.get("LANGSMITH_TRACING", "true")
LANGSMITH_API_KEY = os.environ.get("LANGSMITH_API_KEY")
LANGSMITH_ENDPOINT = os.environ.get("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
LANGSMITH_PROJECT = os.environ.get("LANGSMITH_PROJECT", "RAG_Agent")

# Model Configuration
AGENT_MODEL = os.environ.get("AGENT_MODEL", "gpt-4-turbo")
GRADER_MODEL = os.environ.get("GRADER_MODEL", "gpt-4o")
REWRITE_MODEL = os.environ.get("REWRITE_MODEL", "gpt-4-0125-preview")
GENERATOR_MODEL = os.environ.get("GENERATOR_MODEL", "gpt-4o-mini")

# Default URLs for document retrieval
DEFAULT_URLS = [
    "https://lilianweng.github.io/posts/2023-06-23-agent/",
    "https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/",
    "https://lilianweng.github.io/posts/2023-10-25-adv-attack-llm/",
]

# Vector database configuration
VECTOR_DB_COLLECTION = "rag-chroma"
CHUNK_SIZE = 100
CHUNK_OVERLAP = 50

# Set environment variables
def setup_environment():
    """Set up environment variables for the application."""
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
    os.environ["LANGSMITH_TRACING"] = LANGSMITH_TRACING
    
    if LANGSMITH_API_KEY:
        os.environ["LANGSMITH_API_KEY"] = LANGSMITH_API_KEY
        
    os.environ["LANGSMITH_ENDPOINT"] = LANGSMITH_ENDPOINT
    os.environ["LANGSMITH_PROJECT"] = LANGSMITH_PROJECT