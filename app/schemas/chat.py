"""
Chat Schemas
Pydantic models for chat queries and responses.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class ChatQuery(BaseModel):
    """Schema for chat query request"""
    query: str = Field(..., min_length=1, max_length=1000, description="User question")


class SourceDocument(BaseModel):
    """Schema for source document reference"""
    document_id: int
    filename: str
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Similarity score")


class ChatResponse(BaseModel):
    """Schema for chat response"""
    query: str
    response: str
    sources: List[SourceDocument] = Field(default_factory=list, description="Source documents used")
    cached: bool = Field(default=False, description="Whether response was cached")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatHistoryItem(BaseModel):
    """Schema for chat history item"""
    id: int
    query: str
    response: str
    sources: Optional[List[dict]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatHistoryList(BaseModel):
    """Schema for chat history list"""
    history: List[ChatHistoryItem]
    total: int
