"""
Authentication API Endpoints
User registration and login endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import UserCreate, LoginRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    
    - **email**: Valid email address
    - **password**: Minimum 8 characters
    - **role**: Optional, defaults to "user" (can be "admin")
    
    Returns JWT access token and user information.
    """
    auth_service = AuthService(db)
    return auth_service.register_user(user_data)


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and get JWT token.
    
    - **email**: User email
    - **password**: User password
    
    Returns JWT access token for subsequent authenticated requests.
    """
    auth_service = AuthService(db)
    return auth_service.login(credentials.email, credentials.password)
