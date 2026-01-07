"""
AI Knowledge Assistant - Main Application
FastAPI application with RAG-based document Q&A system.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db
from app.api.v1 import auth, documents, chat
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events.
    
    Startup: Initialize database tables
    Shutdown: Cleanup resources
    """
    # Startup
    logger.info("Starting AI Knowledge Assistant...")
    logger.info(f"Environment: {'DEBUG' if settings.DEBUG else 'PRODUCTION'}")
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Knowledge Assistant...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    **AI Knowledge Assistant** - Enterprise RAG-based Document Q&A System
    
    ## Features
    
    * 🔐 **JWT Authentication** - Secure user authentication with role-based access
    * 📄 **Document Upload** - Upload PDF/TXT documents for indexing
    * 🧠 **RAG System** - Retrieval-Augmented Generation with FAISS and OpenAI
    * 💬 **Intelligent Chat** - Ask questions based on uploaded documents
    * 📊 **Chat History** - Persistent conversation history
    * ⚡ **Redis Caching** - Fast response caching
    
    ## Authentication
    
    Most endpoints require authentication. Use `/api/v1/auth/register` or `/api/v1/auth/login` 
    to get a JWT token, then include it in the Authorization header:
    
    ```
    Authorization: Bearer <your_token>
    ```
    
    ## Workflow
    
    1. Register/Login to get JWT token
    2. Upload documents (PDF/TXT)
    3. Ask questions via chat endpoint
    4. View chat history
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


# Include routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(documents.router, prefix=settings.API_V1_PREFIX)
app.include_router(chat.router, prefix=settings.API_V1_PREFIX)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns application status and version.
    """
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "AI Knowledge Assistant API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
