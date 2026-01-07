"""
Chat Repository
Data access layer for ChatHistory model operations.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.chat import ChatHistory


class ChatRepository:
    """
    Repository pattern for ChatHistory database operations.
    """
    
    def __init__(self, db: Session):
        """
        Initialize repository with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def create(
        self,
        user_id: int,
        query: str,
        response: str,
        sources: Optional[List[dict]] = None
    ) -> ChatHistory:
        """
        Create a new chat history entry.
        
        Args:
            user_id: User ID
            query: User's question
            response: AI's answer
            sources: Optional list of source documents
            
        Returns:
            Created ChatHistory object
        """
        chat = ChatHistory(
            user_id=user_id,
            query=query,
            response=response,
            sources=sources or []
        )
        self.db.add(chat)
        self.db.commit()
        self.db.refresh(chat)
        return chat
    
    def get_by_id(self, chat_id: int) -> Optional[ChatHistory]:
        """
        Get chat history entry by ID.
        
        Args:
            chat_id: Chat history ID
            
        Returns:
            ChatHistory object or None
        """
        return self.db.query(ChatHistory).filter(ChatHistory.id == chat_id).first()
    
    def get_history_by_user(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[ChatHistory]:
        """
        Get chat history for a specific user.
        
        Args:
            user_id: User ID
            limit: Maximum number of entries to return
            offset: Number of entries to skip
            
        Returns:
            List of ChatHistory objects ordered by most recent first
        """
        return (
            self.db.query(ChatHistory)
            .filter(ChatHistory.user_id == user_id)
            .order_by(desc(ChatHistory.created_at))
            .limit(limit)
            .offset(offset)
            .all()
        )
    
    def delete(self, chat_id: int) -> bool:
        """
        Delete a chat history entry.
        
        Args:
            chat_id: Chat history ID
            
        Returns:
            True if deleted, False if not found
        """
        chat = self.get_by_id(chat_id)
        if chat:
            self.db.delete(chat)
            self.db.commit()
            return True
        return False
