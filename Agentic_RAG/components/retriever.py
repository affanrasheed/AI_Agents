import logging
from typing import List, Optional
from langchain.tools.retriever import create_retriever_tool
from components.vectorstore import VectorStoreManager

logger = logging.getLogger(__name__)

class RetrieverToolFactory:
    """Factory for creating retriever tools."""
    
    def __init__(self, vector_store_manager: Optional[VectorStoreManager] = None):
        """
        Initialize the retriever tool factory.
        
        Args:
            vector_store_manager: Vector store manager to use
        """
        self.vector_store_manager = vector_store_manager or VectorStoreManager()
        self._tools = []
        
    def create_retriever_tool(self, 
                             name: str = "retrieve_blog_posts", 
                             description: str = "Search and return information about Lilian Weng blog posts on LLM agents, prompt engineering, and adversarial attacks on LLMs."):
        """
        Create a retriever tool.
        
        Args:
            name: Name of the retriever tool
            description: Description of the retriever tool
            
        Returns:
            Retriever tool
        """
        if self.vector_store_manager.retriever is None:
            logger.warning("Retriever not available, cannot create retriever tool")
            return None
            
        logger.info(f"Creating retriever tool: {name}")
        
        retriever_tool = create_retriever_tool(
            self.vector_store_manager.retriever,
            name,
            description,
        )
        
        # Add to tools list
        self._tools.append(retriever_tool)
        
        return retriever_tool
        
    @property
    def tools(self) -> List:
        """
        Get all created tools.
        
        Returns:
            List of tools
        """
        return self._tools