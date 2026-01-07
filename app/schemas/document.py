"""
Document Schemas
Pydantic models for document upload and retrieval.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class DocumentUpload(BaseModel):
    """Schema for document upload response"""
    id: int
    filename: str
    user_id: int
    created_at: datetime
    message: str = Field(default="Document uploaded and indexed successfully")


class DocumentResponse(BaseModel):
    """Schema for document data"""
    id: int
    filename: str
    user_id: int
    created_at: datetime
    content_preview: Optional[str] = Field(None, description="First 200 characters of content")
    
    class Config:
        from_attributes = True


class DocumentList(BaseModel):
    """Schema for list of documents"""
    documents: list[DocumentResponse]
    total: int
