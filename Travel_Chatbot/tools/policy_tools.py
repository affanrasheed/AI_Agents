"""
Policy lookup tools for the Travel Assistant.
"""
import re
from typing import List, Dict, Any

import numpy as np
import openai
import requests
from langchain_core.tools import tool

import config


class VectorStoreRetriever:
    """
    A simple vector store retriever using OpenAI embeddings.
    """
    def __init__(self, docs: List[Dict[str, Any]], vectors: List[List[float]], oai_client):
        """
        Initialize the retriever with documents, their vectors, and an OpenAI client.
        
        Args:
            docs: List of documents with "page_content" field
            vectors: List of embedding vectors for each document
            oai_client: OpenAI client instance
        """
        self._arr = np.array(vectors)
        self._docs = docs
        self._client = oai_client

    @classmethod
    def from_docs(cls, docs: List[Dict[str, Any]], oai_client):
        """
        Create a VectorStoreRetriever from documents.
        
        Args:
            docs: List of documents with "page_content" field
            oai_client: OpenAI client instance
            
        Returns:
            VectorStoreRetriever instance
        """
        embeddings = oai_client.embeddings.create(
            model="text-embedding-3-small", input=[doc["page_content"] for doc in docs]
        )
        vectors = [emb.embedding for emb in embeddings.data]
        return cls(docs, vectors, oai_client)

    def query(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Query the vector store for documents similar to the query.
        
        Args:
            query: Query string
            k: Number of results to return
            
        Returns:
            List of documents with similarity scores
        """
        embed = self._client.embeddings.create(
            model="text-embedding-3-small", input=[query]
        )
        # Matrix multiplication to get similarity scores
        scores = np.array(embed.data[0].embedding) @ self._arr.T
        top_k_idx = np.argpartition(scores, -k)[-k:]
        top_k_idx_sorted = top_k_idx[np.argsort(-scores[top_k_idx])]
        return [
            {**self._docs[idx], "similarity": scores[idx]} for idx in top_k_idx_sorted
        ]


def load_policy_documents() -> List[Dict[str, str]]:
    """
    Load policy documents from the URL specified in config.
    
    Returns:
        List of document dictionaries with page_content field
    """
    response = requests.get(config.POLICY_URL)
    response.raise_for_status()
    faq_text = response.text
    
    # Split the document into sections based on markdown headers
    docs = [{"page_content": txt} for txt in re.split(r"(?=\n##)", faq_text)]
    return docs


# Initialize the retriever when this module is imported
_docs = load_policy_documents()
_retriever = None


def get_retriever() -> VectorStoreRetriever:
    """
    Get or create the VectorStoreRetriever.
    
    Returns:
        VectorStoreRetriever instance
    """
    global _retriever
    if _retriever is None:
        _retriever = VectorStoreRetriever.from_docs(_docs, openai.Client())
    return _retriever


@tool
def lookup_policy(query: str) -> str:
    """
    Consult the company policies to check whether certain options are permitted.
    Use this before making any flight changes performing other 'write' events.
    
    Args:
        query: The policy question to look up
        
    Returns:
        Relevant policy information
    """
    retriever = get_retriever()
    docs = retriever.query(query, k=2)
    return "\n\n".join([doc["page_content"] for doc in docs])