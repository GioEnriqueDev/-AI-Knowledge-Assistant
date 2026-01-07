"""
Chat API Endpoints
RAG-based chat query and history endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.chat import ChatQuery, ChatResponse, ChatHistoryList, ChatHistoryItem, SourceDocument
from app.services.chat_service import get_chat_service
from app.repositories.chat_repository import ChatRepository

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/query", response_model=ChatResponse)
async def query_chat(
    query: ChatQuery,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ask a question to the AI assistant.
    
    The system will:
    1. Search for relevant document chunks using RAG
    2. Build a controlled prompt with context
    3. Generate an answer using OpenAI
    4. Save to chat history
    5. Cache the response
    
    **The AI will ONLY answer based on uploaded documents.**
    
    **Requires authentication.**
    """
    chat_service = get_chat_service()
    
    # Get response from chat service
    response_text, sources, cached = chat_service.query(query.query)
    
    # Save to chat history (if not cached)
    if not cached:
        chat_repo = ChatRepository(db)
        chat_repo.create(
            user_id=current_user.id,
            query=query.query,
            response=response_text,
            sources=[{
                "document_id": s["document_id"],
                "filename": s["filename"],
                "relevance_score": s["relevance_score"]
            } for s in sources]
        )
    
    # Format sources for response
    source_docs = [
        SourceDocument(
            document_id=s["document_id"],
            filename=s["filename"],
            relevance_score=s["relevance_score"]
        )
        for s in sources
    ]
    
    return ChatResponse(
        query=query.query,
        response=response_text,
        sources=source_docs,
        cached=cached,
        timestamp=datetime.utcnow()
    )


@router.get("/history", response_model=ChatHistoryList)
async def get_chat_history(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get chat history for the current user.
    
    - **limit**: Maximum number of entries (default 50)
    - **offset**: Number of entries to skip (for pagination)
    
    Returns chat history ordered by most recent first.
    
    **Requires authentication.**
    """
    chat_repo = ChatRepository(db)
    history = chat_repo.get_history_by_user(
        user_id=current_user.id,
        limit=limit,
        offset=offset
    )
    
    history_items = [
        ChatHistoryItem(
            id=chat.id,
            query=chat.query,
            response=chat.response,
            sources=chat.sources,
            created_at=chat.created_at
        )
        for chat in history
    ]
    
    return ChatHistoryList(
        history=history_items,
        total=len(history_items)
    )
