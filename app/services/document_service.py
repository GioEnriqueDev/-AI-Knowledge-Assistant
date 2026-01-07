"""
Document Service
Business logic for document upload and processing.
"""

from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.repositories.document_repository import DocumentRepository
from app.services.rag_service import get_rag_service
from app.utils.text_extractor import extract_text_from_file
from app.utils.logger import logger
from app.core.config import settings


class DocumentService:
    """
    Service for handling document upload and indexing.
    """
    
    def __init__(self, db: Session):
        """
        Initialize document service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.doc_repo = DocumentRepository(db)
        self.rag_service = get_rag_service()
    
    async def upload_document(self, file: UploadFile, user_id: int):
        """
        Upload and index a document.
        
        Args:
            file: Uploaded file
            user_id: Owner user ID
            
        Returns:
            Document: Created document object
            
        Raises:
            HTTPException: If file validation or processing fails
        """
        # Validate file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        if file_size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE / 1024 / 1024}MB"
            )
        
        # Validate file extension
        filename = file.filename.lower()
        if not any(filename.endswith(ext) for ext in settings.ALLOWED_EXTENSIONS):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )
        
        logger.info(f"Processing document upload: {file.filename} for user {user_id}")
        
        # Extract text content
        content = await extract_text_from_file(file)
        
        if len(content.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Document content is too short or empty"
            )
        
        # Save document to database
        document = self.doc_repo.create(
            filename=file.filename,
            content=content,
            user_id=user_id
        )
        
        # Index document for RAG
        try:
            embedding_id = self.rag_service.index_document(
                document_id=document.id,
                filename=document.filename,
                content=content
            )
            
            # Update document with embedding ID
            document.embedding_id = embedding_id
            self.db.commit()
            
            logger.info(f"Successfully uploaded and indexed document: {file.filename}")
            
        except Exception as e:
            logger.error(f"Error indexing document: {e}")
            # Document is saved but not indexed - could be handled differently
            raise HTTPException(
                status_code=500,
                detail=f"Document saved but indexing failed: {str(e)}"
            )
        
        return document
