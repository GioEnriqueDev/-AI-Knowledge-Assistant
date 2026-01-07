"""
RAG Service with Ollama
Retrieval-Augmented Generation implementation using FAISS and Ollama embeddings.
"""

import os
import pickle
from typing import List, Tuple, Optional
import faiss
import numpy as np
from langchain.text_splitter import RecursiveCharacterTextSplitter
import requests

from app.core.config import settings
from app.utils.logger import logger


class RAGService:
    """
    RAG (Retrieval-Augmented Generation) service for document indexing and retrieval.
    
    Uses FAISS for vector similarity search and Ollama for embeddings.
    """
    
    def __init__(self):
        """Initialize RAG service with Ollama client and FAISS index."""
        self.ollama_url = settings.OLLAMA_BASE_URL
        self.embedding_model = settings.OLLAMA_EMBEDDING_MODEL
        self.index: Optional[faiss.IndexFlatL2] = None
        self.documents: List[dict] = []  # Store document chunks with metadata
        self.dimension = 768  # nomic-embed-text dimension
        
        # Text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
        )
        
        # Try to load existing index
        self._load_index()
    
    def _load_index(self) -> None:
        """Load FAISS index and documents from disk if they exist."""
        index_path = "faiss_index.bin"
        docs_path = "faiss_documents.pkl"
        
        if os.path.exists(index_path) and os.path.exists(docs_path):
            try:
                self.index = faiss.read_index(index_path)
                with open(docs_path, 'rb') as f:
                    self.documents = pickle.load(f)
                logger.info(f"Loaded FAISS index with {len(self.documents)} documents")
            except Exception as e:
                logger.warning(f"Could not load FAISS index: {e}")
                self._initialize_index()
        else:
            self._initialize_index()
    
    def _initialize_index(self) -> None:
        """Initialize a new FAISS index."""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []
        logger.info("Initialized new FAISS index")
    
    def _save_index(self) -> None:
        """Save FAISS index and documents to disk."""
        try:
            faiss.write_index(self.index, "faiss_index.bin")
            with open("faiss_documents.pkl", 'wb') as f:
                pickle.dump(self.documents, f)
            logger.info("Saved FAISS index to disk")
        except Exception as e:
            logger.error(f"Error saving FAISS index: {e}")
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """
        Get embedding vector for text using Ollama API.
        
        Args:
            text: Text to embed
            
        Returns:
            np.ndarray: Embedding vector
        """
        try:
            response = requests.post(
                f"{self.ollama_url}/api/embeddings",
                json={
                    "model": self.embedding_model,
                    "prompt": text
                }
            )
            response.raise_for_status()
            embedding = np.array(response.json()["embedding"], dtype='float32')
            return embedding
        except Exception as e:
            logger.error(f"Error getting embedding from Ollama: {e}")
            raise
    
    def index_document(self, document_id: int, filename: str, content: str) -> str:
        """
        Index a document by chunking and creating embeddings.
        
        Args:
            document_id: Database document ID
            filename: Document filename
            content: Document text content
            
        Returns:
            str: Embedding ID (for reference)
        """
        logger.info(f"Indexing document: {filename} (ID: {document_id})")
        
        # Split document into chunks
        chunks = self.text_splitter.split_text(content)
        logger.info(f"Split document into {len(chunks)} chunks")
        
        # Create embeddings for each chunk
        embeddings = []
        for i, chunk in enumerate(chunks):
            embedding = self._get_embedding(chunk)
            embeddings.append(embedding)
            
            # Store chunk metadata
            self.documents.append({
                "document_id": document_id,
                "filename": filename,
                "chunk_index": i,
                "content": chunk
            })
        
        # Add embeddings to FAISS index
        embeddings_array = np.array(embeddings, dtype='float32')
        self.index.add(embeddings_array)
        
        # Save index
        self._save_index()
        
        embedding_id = f"doc_{document_id}_{len(chunks)}_chunks"
        logger.info(f"Successfully indexed document: {embedding_id}")
        
        return embedding_id
    
    def search_similar(self, query: str, top_k: int = None) -> List[Tuple[dict, float]]:
        """
        Search for similar document chunks using semantic similarity.
        
        Args:
            query: Search query
            top_k: Number of results to return (default from settings)
            
        Returns:
            List of tuples (document_chunk, similarity_score)
        """
        if top_k is None:
            top_k = settings.TOP_K_RESULTS
        
        if self.index.ntotal == 0:
            logger.warning("FAISS index is empty, no documents to search")
            return []
        
        # Get query embedding
        query_embedding = self._get_embedding(query)
        query_vector = np.array([query_embedding], dtype='float32')
        
        # Search FAISS index
        distances, indices = self.index.search(query_vector, min(top_k, self.index.ntotal))
        
        # Prepare results with similarity scores
        results = []
        for distance, idx in zip(distances[0], indices[0]):
            if idx < len(self.documents):
                # Convert L2 distance to similarity score (inverse)
                similarity = 1 / (1 + distance)
                results.append((self.documents[idx], float(similarity)))
        
        logger.info(f"Found {len(results)} similar chunks for query")
        return results
    
    def get_context_for_query(self, query: str) -> Tuple[str, List[dict]]:
        """
        Get relevant context for a query by retrieving similar documents.
        
        Args:
            query: User query
            
        Returns:
            Tuple of (context_text, source_documents)
        """
        similar_chunks = self.search_similar(query)
        
        if not similar_chunks:
            return "", []
        
        # Build context from chunks
        context_parts = []
        sources = []
        seen_docs = set()
        
        for chunk_data, score in similar_chunks:
            context_parts.append(chunk_data["content"])
            
            # Track unique source documents
            doc_id = chunk_data["document_id"]
            if doc_id not in seen_docs:
                sources.append({
                    "document_id": doc_id,
                    "filename": chunk_data["filename"],
                    "relevance_score": score
                })
                seen_docs.add(doc_id)
        
        context = "\n\n---\n\n".join(context_parts)
        return context, sources


# Singleton instance
_rag_service_instance: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """
    Get singleton RAG service instance.
    
    Returns:
        RAGService: Shared RAG service instance
    """
    global _rag_service_instance
    if _rag_service_instance is None:
        _rag_service_instance = RAGService()
    return _rag_service_instance
