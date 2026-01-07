"""
User Repository
Data access layer for User model operations.
"""

from typing import Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import hash_password


class UserRepository:
    """
    Repository pattern for User database operations.
    
    Separates data access logic from business logic.
    """
    
    def __init__(self, db: Session):
        """
        Initialize repository with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User object or None if not found
        """
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            email: User email
            
        Returns:
            User object or None if not found
        """
        return self.db.query(User).filter(User.email == email).first()
    
    def create(self, email: str, password: str, role: str = "user") -> User:
        """
        Create a new user.
        
        Args:
            email: User email
            password: Plain text password (will be hashed)
            role: User role (default: "user")
            
        Returns:
            Created User object
        """
        hashed_password = hash_password(password)
        user = User(
            email=email,
            hashed_password=hashed_password,
            role=role
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete(self, user_id: int) -> bool:
        """
        Delete a user by ID.
        
        Args:
            user_id: User ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        user = self.get_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False
