import logging
from typing import List, Optional
from langchain_community.vectorstores import Chroma
from components.embeddings import EmbeddingManager
from core.config import VECTOR_DB_COLLECTION

logger = logging.getLogger(__name__)

class VectorStoreManager:
    """Manager for vector store operations."""
    
    def __init__(self, collection_name: str = VECTOR_DB_COLLECTION, embedding_manager: Optional[EmbeddingManager] = None):
        """
        Initialize the vector store manager.
        
        Args:
            collection_name: Name of the vector store collection
            embedding_manager: Embedding manager to use
        """
        self.collection_name = collection_name
        self.embedding_manager = embedding_manager or EmbeddingManager()
        self._vectorstore = None
        self._retriever = None
        
    def create_from_documents(self, documents: List):
        """
        Create a vector store from documents.
        
        Args:
            documents: List of documents to add to the vector store
            
        Returns:
            Self for method chaining
        """
        if not documents:
            logger.warning("No documents provided for vector store creation")
            return self
            
        logger.info(f"Creating vector store with {len(documents)} documents")
        
        try:
            self._vectorstore = Chroma.from_documents(
                documents=documents,
                collection_name=self.collection_name,
                embedding=self.embedding_manager.embeddings,
            )
            logger.info(f"Vector store created with collection name: {self.collection_name}")
            
            # Reset retriever when vectorstore changes
            self._retriever = None
            
            return self
            
        except Exception as e:
            logger.error(f"Error creating vector store: {e}")
            raise
            
    @property
    def vectorstore(self):
        """
        Get the vector store.
        
        Returns:
            Vector store instance
        """
        if self._vectorstore is None:
            logger.warning("Vector store not initialized")
            
        return self._vectorstore
        
    @property
    def retriever(self):
        """
        Get or create retriever from the vector store.
        
        Returns:
            Retriever instance
        """
        if self._vectorstore is None:
            logger.warning("Vector store not initialized, cannot create retriever")
            return None
            
        if self._retriever is None:
            logger.info("Creating retriever from vector store")
            self._retriever = self._vectorstore.as_retriever()
            
        return self._retriever