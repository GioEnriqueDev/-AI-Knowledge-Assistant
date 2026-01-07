"""
Authentication Service
Business logic for user authentication and JWT token management.
"""

from datetime import timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository
from app.core.security import verify_password, create_access_token
from app.schemas.auth import UserCreate, TokenResponse
from app.utils.logger import logger


class AuthService:
    """
    Service for authentication operations.
    """
    
    def __init__(self, db: Session):
        """
        Initialize auth service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.user_repo = UserRepository(db)
    
    def register_user(self, user_data: UserCreate) -> TokenResponse:
        """
        Register a new user.
        
        Args:
            user_data: User registration data
            
        Returns:
            TokenResponse: JWT token and user info
            
        Raises:
            HTTPException: If email already exists
        """
        # Check if user already exists
        existing_user = self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        user = self.user_repo.create(
            email=user_data.email,
            password=user_data.password,
            role=user_data.role or "user"
        )
        
        logger.info(f"New user registered: {user.email}")
        
        # Generate JWT token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user.id,
            email=user.email,
            role=user.role
        )
    
    def login(self, email: str, password: str) -> TokenResponse:
        """
        Authenticate user and generate JWT token.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            TokenResponse: JWT token and user info
            
        Raises:
            HTTPException: If credentials are invalid
        """
        # Get user by email
        user = self.user_repo.get_by_email(email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        logger.info(f"User logged in: {user.email}")
        
        # Generate JWT token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user.id,
            email=user.email,
            role=user.role
        )
