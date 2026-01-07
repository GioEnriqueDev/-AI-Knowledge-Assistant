"""
Document Repository
Data access layer for Document model operations.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.document import Document


class DocumentRepository:
    """
    Repository pattern for Document database operations.
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
        filename: str,
        content: str,
        user_id: int,
        embedding_id: Optional[str] = None
    ) -> Document:
        """
        Create a new document.
        
        Args:
            filename: Original filename
            content: Extracted text content
            user_id: Owner user ID
            embedding_id: Optional FAISS embedding reference
            
        Returns:
            Created Document object
        """
        document = Document(
            filename=filename,
            content=content,
            user_id=user_id,
            embedding_id=embedding_id
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document
    
    def get_by_id(self, document_id: int) -> Optional[Document]:
        """
        Get document by ID.
        
        Args:
            document_id: Document ID
            
        Returns:
            Document object or None
        """
        return self.db.query(Document).filter(Document.id == document_id).first()
    
    def get_all_by_user(self, user_id: int) -> List[Document]:
        """
        Get all documents for a specific user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of Document objects
        """
        return self.db.query(Document).filter(Document.user_id == user_id).all()
    
    def get_all(self) -> List[Document]:
        """
        Get all documents (admin only).
        
        Returns:
            List of all Document objects
        """
        return self.db.query(Document).all()
    
    def delete(self, document_id: int) -> bool:
        """
        Delete a document by ID.
        
        Args:
            document_id: Document ID
            
        Returns:
            True if deleted, False if not found
        """
        document = self.get_by_id(document_id)
        if document:
            self.db.delete(document)
            self.db.commit()
            return True
        return False
