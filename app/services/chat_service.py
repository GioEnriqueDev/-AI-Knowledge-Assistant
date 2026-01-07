"""
Chat Service with Ollama
Orchestrates RAG-based chat functionality with Ollama and Redis caching.
"""

import json
import hashlib
from typing import Optional, Tuple, List
import requests
import redis

from app.core.config import settings
from app.services.rag_service import get_rag_service
from app.utils.logger import logger


class ChatService:
    """
    Chat service that combines RAG retrieval with Ollama chat completion.
    
    Implements caching to avoid redundant API calls.
    """
    
    def __init__(self):
        """Initialize chat service with Ollama client and optional Redis cache."""
        self.ollama_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self.rag_service = get_rag_service()
        
        # Initialize Redis cache if enabled
        self.redis_client: Optional[redis.Redis] = None
        if settings.REDIS_ENABLED:
            try:
                self.redis_client = redis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB,
                    decode_responses=True
                )
                self.redis_client.ping()
                logger.info("Connected to Redis cache")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}. Caching disabled.")
                self.redis_client = None
    
    def _get_cache_key(self, query: str) -> str:
        """
        Generate cache key for a query.
        
        Args:
            query: User query
            
        Returns:
            str: Cache key (hash of query)
        """
        return f"chat:{hashlib.md5(query.encode()).hexdigest()}"
    
    def _get_cached_response(self, query: str) -> Optional[dict]:
        """
        Get cached response for a query.
        
        Args:
            query: User query
            
        Returns:
            dict: Cached response or None
        """
        if not self.redis_client:
            return None
        
        try:
            cache_key = self._get_cache_key(query)
            cached = self.redis_client.get(cache_key)
            if cached:
                logger.info(f"Cache hit for query: {query[:50]}...")
                return json.loads(cached)
        except Exception as e:
            logger.error(f"Error reading from cache: {e}")
        
        return None
    
    def _cache_response(self, query: str, response: dict) -> None:
        """
        Cache a response.
        
        Args:
            query: User query
            response: Response to cache
        """
        if not self.redis_client:
            return
        
        try:
            cache_key = self._get_cache_key(query)
            self.redis_client.setex(
                cache_key,
                settings.CACHE_TTL,
                json.dumps(response)
            )
            logger.info(f"Cached response for query: {query[:50]}...")
        except Exception as e:
            logger.error(f"Error writing to cache: {e}")
    
    def _build_prompt(self, query: str, context: str) -> str:
        """
        Build a controlled prompt for Ollama to prevent hallucinations.
        
        Args:
            query: User query
            context: Retrieved context from documents
            
        Returns:
            str: Formatted prompt
        """
        prompt = f"""You are an AI assistant that answers questions based ONLY on the provided context from uploaded documents.

CRITICAL RULES:
1. Answer ONLY using information from the context below
2. If the context doesn't contain relevant information, say "I don't have enough information in the uploaded documents to answer this question."
3. Do NOT use external knowledge or make assumptions
4. Cite specific parts of the context when answering
5. Be concise and accurate

CONTEXT FROM DOCUMENTS:
{context}

USER QUESTION:
{query}

ANSWER:"""
        
        return prompt
    
    def query(self, user_query: str) -> Tuple[str, List[dict], bool]:
        """
        Process a user query using RAG.
        
        Args:
            user_query: User's question
            
        Returns:
            Tuple of (response, sources, cached)
        """
        logger.info(f"Processing query: {user_query[:100]}...")
        
        # Check cache first
        cached = self._get_cached_response(user_query)
        if cached:
            return cached["response"], cached["sources"], True
        
        # Get relevant context from documents
        context, sources = self.rag_service.get_context_for_query(user_query)
        
        if not context:
            response = "I don't have any documents to answer your question. Please upload some documents first."
            return response, [], False
        
        # Build prompt with context
        prompt = self._build_prompt(user_query, context)
        
        # Get response from Ollama
        try:
            response_data = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": settings.OLLAMA_TEMPERATURE,
                        "num_predict": settings.OLLAMA_MAX_TOKENS
                    }
                }
            )
            response_data.raise_for_status()
            
            response = response_data.json()["response"].strip()
            logger.info("Successfully generated response from Ollama")
            
        except Exception as e:
            logger.error(f"Error calling Ollama API: {e}")
            response = f"Error generating response: {str(e)}"
            sources = []
        
        # Cache the response
        cache_data = {"response": response, "sources": sources}
        self._cache_response(user_query, cache_data)
        
        return response, sources, False


# Singleton instance
_chat_service_instance: Optional[ChatService] = None


def get_chat_service() -> ChatService:
    """
    Get singleton chat service instance.
    
    Returns:
        ChatService: Shared chat service instance
    """
    global _chat_service_instance
    if _chat_service_instance is None:
        _chat_service_instance = ChatService()
    return _chat_service_instance
