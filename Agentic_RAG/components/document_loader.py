from typing import List, Optional
import logging
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from core.config import CHUNK_SIZE, CHUNK_OVERLAP

logger = logging.getLogger(__name__)

class DocumentLoader:
    """Document loader for retrieving and splitting web documents."""
    
    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
        """
        Initialize the document loader.
        
        Args:
            chunk_size: Size of document chunks
            chunk_overlap: Overlap between document chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=self.chunk_size, 
            chunk_overlap=self.chunk_overlap
        )
        
    def load_from_urls(self, urls: List[str]) -> List:
        """
        Load documents from a list of URLs.
        
        Args:
            urls: List of URLs to load documents from
            
        Returns:
            List of loaded and split documents
        """
        logger.info(f"Loading documents from {len(urls)} URLs...")
        
        try:
            # Load documents from URLs
            docs = [WebBaseLoader(url).load() for url in urls]
            # Flatten the list of lists
            docs_list = [item for sublist in docs for item in sublist]
            logger.info(f"Loaded {len(docs_list)} documents")
            
            # Split documents
            return self.split_documents(docs_list)
            
        except Exception as e:
            logger.error(f"Error loading documents: {e}")
            return []
            
    def split_documents(self, documents: List) -> List:
        """
        Split documents into chunks.
        
        Args:
            documents: List of documents to split
            
        Returns:
            List of split documents
        """
        logger.info(f"Splitting {len(documents)} documents...")
        
        try:
            doc_splits = self.text_splitter.split_documents(documents)
            logger.info(f"Split into {len(doc_splits)} chunks")
            return doc_splits
            
        except Exception as e:
            logger.error(f"Error splitting documents: {e}")
            return []