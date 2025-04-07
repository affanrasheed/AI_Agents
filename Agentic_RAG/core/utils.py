import getpass
import os
import logging
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def set_env_with_prompt(key: str) -> None:
    """
    Set environment variable, prompting user for input if not already set.
    
    Args:
        key: The environment variable key to set
    """
    if key not in os.environ:
        value = getpass.getpass(f"{key}: ")
        os.environ[key] = value
        logger.info(f"Environment variable {key} set")

def format_docs_for_display(docs: List[Any]) -> str:
    """
    Format documents for display in the UI.
    
    Args:
        docs: List of documents to format
        
    Returns:
        Formatted string representation of documents
    """
    if not docs:
        return "No documents found."
        
    formatted = []
    for i, doc in enumerate(docs):
        content = getattr(doc, "page_content", str(doc))
        metadata = getattr(doc, "metadata", {})
        source = metadata.get("source", "Unknown source")
        
        formatted.append(f"Document {i+1} (Source: {source})\n{'-' * 40}\n{content}\n")
        
    return "\n\n".join(formatted)

def format_chat_message(message: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format a chat message for display in the UI.
    
    Args:
        message: Message to format
        
    Returns:
        Formatted message
    """
    role = message.get("role", "")
    if hasattr(message, "content"):
        content = message.content
    else:
        content = message.get("content", "")
        
    # Format role for display
    display_role = role.capitalize()
    if role == "system":
        display_role = "System"
    elif role == "user":
        display_role = "You"
    elif role == "assistant":
        display_role = "Assistant"
        
    return {
        "role": role,
        "display_role": display_role,
        "content": content
    }

def truncate_text(text: str, max_length: int = 300) -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length of the truncated text
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
        
    return text[:max_length] + "..."