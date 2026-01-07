"""
Chat History Model
Stores conversation history between users and the AI assistant.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class ChatHistory(Base):
    """
    Chat history model for storing user queries and AI responses.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to user
        query: User's question
        response: AI's answer
        sources: JSON array of source document IDs used
        created_at: Query timestamp
        user: Relationship to User
    """
    
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    sources = Column(JSON, nullable=True)  # List of document IDs used for context
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="chat_history")
    
    def __repr__(self) -> str:
        return f"<ChatHistory(id={self.id}, user_id={self.user_id}, created_at={self.created_at})>"
