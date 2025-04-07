import logging
from langchain_openai import OpenAIEmbeddings
from core.config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

class EmbeddingManager:
    """Manager for embeddings operations."""
    
    def __init__(self, api_key: str = OPENAI_API_KEY, model: str = None):
        """
        Initialize the embeddings manager.
        
        Args:
            api_key: OpenAI API key
            model: OpenAI embedding model to use
        """
        self.api_key = api_key
        self.model = model
        self._embeddings = None
        
    @property
    def embeddings(self):
        """
        Get or create OpenAI embeddings instance.
        
        Returns:
            OpenAIEmbeddings instance
        """
        if self._embeddings is None:
            logger.info("Initializing OpenAI embeddings")
            
            if self.model:
                self._embeddings = OpenAIEmbeddings(
                    openai_api_key=self.api_key,
                    model=self.model
                )
            else:
                self._embeddings = OpenAIEmbeddings(
                    openai_api_key=self.api_key
                )
                
        return self._embeddings