"""
Setup script for initializing the Travel Assistant database.
"""
import os
import sys
from pathlib import Path

# Add the project root to PYTHONPATH
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import config
# Import directly from the module
from database import connection


def setup_database():
    """Download and set up the database with updated dates."""
    print(f"Setting up database from {config.DB_URL}...")
    db_path = connection.download_database(force_download=True)
    print(f"Database downloaded to {db_path}")
    
    print("Updating dates in the database...")
    updated_db = connection.update_dates(db_path)
    print(f"Database updated at {updated_db}")
    
    print("Database setup complete!")


def setup_environment():
    """Create a .env file template if it doesn't exist."""
    env_path = os.path.join(project_root, ".env")
    
    # Create necessary directories if they don't exist
    directories = [
        os.path.join(project_root, "database"),
        os.path.join(project_root, "tools"),
        os.path.join(project_root, "assistant"),
        os.path.join(project_root, "ui"),
        os.path.join(project_root, "ui", "components"),
        os.path.join(project_root, "ui", "pages"),
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
    
    if not os.path.exists(env_path):
        print("Creating .env file template...")
        
        with open(env_path, "w") as f:
            f.write("""# API Keys
ANTHROPIC_API_KEY=
OPENAI_API_KEY= 
TAVILY_API_KEY= 
LANGSMITH_API_KEY= 

# LangSmith configuration
LANGSMITH_TRACING=
LANGSMITH_ENDPOINT=
LANGSMITH_PROJECT=

# LLM Configuration
LLM_MODEL=claude-3-5-haiku-latest
LLM_TEMPERATURE=1.0

# Default passenger ID for testing
DEFAULT_PASSENGER_ID=3442 587242
""")
        
        print(f".env file created at {env_path}")
        print("Please edit the file and add your API keys.")
    else:
        print(f".env file already exists at {env_path}")


if __name__ == "__main__":
    print("Running setup for Travel Assistant...")
    setup_environment()
    setup_database()
    print("Setup complete!")