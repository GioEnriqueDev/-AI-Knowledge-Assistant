"""
Document Model
Represents uploaded documents with their content and embeddings.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Document(Base):
    """
    Document model for storing uploaded files and their content.
    
    Attributes:
        id: Primary key
        filename: Original filename
        content: Extracted text content
        user_id: Foreign key to owner
        embedding_id: Reference to vector store embedding
        created_at: Upload timestamp
        owner: Relationship to User
    """
    
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    embedding_id = Column(String, nullable=True)  # FAISS index reference
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="documents")
    
    def __repr__(self) -> str:
        return f"<Document(id={self.id}, filename={self.filename}, user_id={self.user_id})>"
