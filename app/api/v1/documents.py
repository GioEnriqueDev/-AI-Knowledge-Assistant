"""
Document API Endpoints
Document upload and retrieval endpoints.
"""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.document import DocumentUpload, DocumentResponse, DocumentList
from app.services.document_service import DocumentService
from app.repositories.document_repository import DocumentRepository

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentUpload, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a document (PDF or TXT).
    
    The document will be:
    1. Validated for size and format
    2. Text extracted
    3. Stored in database
    4. Indexed for RAG retrieval
    
    **Requires authentication.**
    """
    doc_service = DocumentService(db)
    document = await doc_service.upload_document(file, current_user.id)
    
    return DocumentUpload(
        id=document.id,
        filename=document.filename,
        user_id=document.user_id,
        created_at=document.created_at,
        message="Document uploaded and indexed successfully"
    )


@router.get("", response_model=DocumentList)
async def get_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all documents for the current user.
    
    Returns list of uploaded documents with metadata.
    
    **Requires authentication.**
    """
    doc_repo = DocumentRepository(db)
    documents = doc_repo.get_all_by_user(current_user.id)
    
    # Add content preview
    doc_responses = []
    for doc in documents:
        preview = doc.content[:200] + "..." if len(doc.content) > 200 else doc.content
        doc_responses.append(
            DocumentResponse(
                id=doc.id,
                filename=doc.filename,
                user_id=doc.user_id,
                created_at=doc.created_at,
                content_preview=preview
            )
        )
    
    return DocumentList(
        documents=doc_responses,
        total=len(doc_responses)
    )
