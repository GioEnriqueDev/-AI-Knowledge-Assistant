# 🧠 AI Knowledge Assistant

**Enterprise-Grade RAG-Based Document Q&A System**

A production-ready backend system that enables intelligent question-answering based on uploaded documents using Retrieval-Augmented Generation (RAG), built with FastAPI, PostgreSQL, Redis, and OpenAI.

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Design Decisions](#-design-decisions)
- [Future Enhancements](#-future-enhancements)

---

## ✨ Features

### Core Functionality
- ✅ **Document Upload & Processing**: PDF and TXT file support with text extraction
- ✅ **RAG Implementation**: FAISS vector store with OpenAI embeddings for semantic search
- ✅ **Intelligent Chat**: Context-aware responses using GPT-4 with anti-hallucination prompts
- ✅ **Chat History**: Persistent conversation storage with source tracking

### Security & Auth
- ✅ **JWT Authentication**: Secure token-based authentication
- ✅ **Role-Based Access Control**: User and Admin roles
- ✅ **Password Hashing**: Bcrypt encryption for secure password storage

### Performance
- ✅ **Redis Caching**: Response caching for faster repeated queries
- ✅ **Connection Pooling**: Optimized database connections
- ✅ **Async Operations**: Non-blocking I/O for better performance

### Developer Experience
- ✅ **Auto-Generated API Docs**: Swagger UI and ReDoc
- ✅ **Type Hints**: Full type annotations throughout
- ✅ **Comprehensive Logging**: Structured logging for debugging
- ✅ **Docker Support**: Containerized deployment with docker-compose

---

## 🏗️ Architecture

### Layered Architecture

```
┌─────────────────────────────────────────┐
│          API Layer (FastAPI)            │
│  ┌──────────┬──────────┬──────────┐    │
│  │   Auth   │Documents │   Chat   │    │
│  └──────────┴──────────┴──────────┘    │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Service Layer (Business Logic)   │
│  ┌──────────┬──────────┬──────────┐    │
│  │   Auth   │ Document │   Chat   │    │
│  │ Service  │ Service  │ Service  │    │
│  └──────────┴──────────┴──────────┘    │
│           ┌──────────┐                  │
│           │   RAG    │                  │
│           │ Service  │                  │
│           └──────────┘                  │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      Repository Layer (Data Access)      │
│  ┌──────────┬──────────┬──────────┐    │
│  │   User   │ Document │   Chat   │    │
│  │   Repo   │   Repo   │   Repo   │    │
│  └──────────┴──────────┴──────────┘    │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Data Layer (Storage)             │
│  ┌──────────┬──────────┬──────────┐    │
│  │PostgreSQL│  Redis   │  FAISS   │    │
│  └──────────┴──────────┴──────────┘    │
└─────────────────────────────────────────┘
```

### RAG Flow

```
User Query → Embedding → FAISS Search → Context Retrieval
                                              ↓
                                    Build Controlled Prompt
                                              ↓
                                    OpenAI Chat Completion
                                              ↓
                                    Response + Sources
```

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Framework** | FastAPI | High-performance async web framework |
| **Database** | PostgreSQL | Relational data storage |
| **Cache** | Redis | Response caching |
| **Vector Store** | FAISS | Similarity search for RAG |
| **AI** | OpenAI API | Embeddings & Chat Completion |
| **Auth** | JWT + Bcrypt | Secure authentication |
| **ORM** | SQLAlchemy | Database abstraction |
| **Validation** | Pydantic | Request/response validation |
| **Deployment** | Docker | Containerization |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- OpenAI API Key

### Option 1: Docker (Recommended)

```bash
# 1. Clone the repository
cd veritas_pro

# 2. Create .env file
# Windows:
copy .env.example .env
# Linux/Mac:
cp .env.example .env

# 3. Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here

# 4. Start all services
# Docker Compose V2 (Docker Desktop):
docker compose up -d

# OR Docker Compose V1:
docker-compose up -d

# 5. Check health
curl http://localhost:8000/health
# OR on Windows PowerShell:
Invoke-WebRequest http://localhost:8000/health

# 6. Access API docs
# Open http://localhost:8000/docs
```

**Troubleshooting Docker:**
- If `docker-compose` not found, use `docker compose` (V2)
- Ensure Docker Desktop is running
- Check Docker version: `docker --version`

### Option 2: Local Development

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup PostgreSQL and Redis locally

# 4. Create .env file
cp .env.example .env
# Edit .env with your configuration

# 5. Run the application
uvicorn app.main:app --reload

# 6. Access API docs
# Open http://localhost:8000/docs
```

---

## 📚 API Documentation

### Authentication

#### Register User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "role": "user"
}
```

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 1,
  "email": "user@example.com",
  "role": "user"
}
```

### Documents

#### Upload Document
```http
POST /api/v1/documents/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <PDF or TXT file>
```

#### Get Documents
```http
GET /api/v1/documents
Authorization: Bearer <token>
```

### Chat

#### Query
```http
POST /api/v1/chat/query
Authorization: Bearer <token>
Content-Type: application/json

{
  "query": "What is the main topic of the uploaded documents?"
}
```

**Response:**
```json
{
  "query": "What is the main topic...",
  "response": "Based on the uploaded documents...",
  "sources": [
    {
      "document_id": 1,
      "filename": "document.pdf",
      "relevance_score": 0.92
    }
  ],
  "cached": false,
  "timestamp": "2024-01-06T12:00:00"
}
```

#### Get History
```http
GET /api/v1/chat/history?limit=50&offset=0
Authorization: Bearer <token>
```

---

## 📁 Project Structure

```
veritas_pro/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── core/
│   │   ├── config.py          # Configuration management
│   │   ├── security.py        # JWT & password hashing
│   │   └── database.py        # SQLAlchemy setup
│   ├── models/
│   │   ├── user.py            # User model
│   │   ├── document.py        # Document model
│   │   └── chat.py            # ChatHistory model
│   ├── schemas/
│   │   ├── auth.py            # Auth request/response schemas
│   │   ├── document.py        # Document schemas
│   │   └── chat.py            # Chat schemas
│   ├── repositories/
│   │   ├── user_repository.py
│   │   ├── document_repository.py
│   │   └── chat_repository.py
│   ├── services/
│   │   ├── auth_service.py    # Authentication logic
│   │   ├── document_service.py # Document processing
│   │   ├── rag_service.py     # RAG implementation
│   │   └── chat_service.py    # Chat orchestration
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py        # Auth endpoints
│   │       ├── documents.py   # Document endpoints
│   │       └── chat.py        # Chat endpoints
│   └── utils/
│       ├── text_extractor.py  # PDF/TXT extraction
│       └── logger.py          # Logging configuration
├── tests/
│   ├── test_auth.py
│   ├── test_documents.py
│   └── test_chat.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── requirements-dev.txt
├── .env.example
└── README.md
```

---

## 💡 Design Decisions

### 1. **Layered Architecture**
- **Why**: Separation of concerns, testability, maintainability
- **Benefit**: Easy to swap implementations (e.g., replace FAISS with pgvector)

### 2. **Repository Pattern**
- **Why**: Abstraction of data access logic
- **Benefit**: Business logic independent of database implementation

### 3. **FAISS for Vector Store**
- **Why**: Simple, fast, no additional database setup
- **Alternative**: pgvector extension for PostgreSQL (production-grade)
- **Trade-off**: FAISS is in-memory, pgvector is persistent

### 4. **Redis Caching**
- **Why**: Reduce OpenAI API costs and improve response time
- **Benefit**: Identical queries return instantly from cache

### 5. **Controlled Prompting**
- **Why**: Prevent AI hallucinations
- **Implementation**: Strict prompt engineering with context-only responses

### 6. **JWT Authentication**
- **Why**: Stateless, scalable authentication
- **Production Note**: Should integrate with Keycloak/AWS Cognito for enterprise

### 7. **Type Hints & Pydantic**
- **Why**: Type safety, auto-validation, better IDE support
- **Benefit**: Catch errors at development time, not runtime

---

## 🔮 Future Enhancements

### Production Readiness
- [ ] **AWS Deployment**: ECS/EKS with RDS and ElastiCache
- [ ] **CI/CD Pipeline**: GitHub Actions with automated testing
- [ ] **Monitoring**: Prometheus + Grafana for metrics
- [ ] **Logging**: ELK Stack for centralized logging

### Authentication
- [ ] **Keycloak Integration**: Enterprise IAM
- [ ] **OAuth2**: Social login support
- [ ] **MFA**: Two-factor authentication

### RAG Improvements
- [ ] **pgvector**: Persistent vector storage
- [ ] **Hybrid Search**: Combine semantic + keyword search
- [ ] **Re-ranking**: Improve retrieval quality
- [ ] **Streaming Responses**: Real-time token streaming

### Features
- [ ] **Multi-tenancy**: Isolated data per organization
- [ ] **Document Versioning**: Track document updates
- [ ] **Batch Processing**: Async document indexing
- [ ] **Export**: PDF reports of chat sessions

### Scalability
- [ ] **Celery**: Background task processing
- [ ] **Load Balancing**: Nginx/Traefik
- [ ] **Horizontal Scaling**: Multiple app instances
- [ ] **Database Sharding**: For large-scale deployments

---

## 🧪 Testing

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v --cov=app

# Type checking
mypy app/

# Code formatting
black app/ tests/
flake8 app/ tests/
```

---

## 📝 Environment Variables

See `.env.example` for all available configuration options.

**Critical Variables:**
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `SECRET_KEY`: JWT secret (change in production)
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_HOST`: Redis server host

---

## 🤝 Contributing

This project follows clean code principles and SOLID design patterns. When contributing:

1. Follow the existing architecture
2. Add type hints to all functions
3. Write docstrings for public APIs
4. Add tests for new features
5. Update documentation

---

## 📄 License

MIT License - See LICENSE file for details

---

## 👨‍💻 Author

Created as a demonstration of enterprise-grade backend development skills for technical interviews.

**Skills Demonstrated:**
- Clean Architecture & SOLID Principles
- FastAPI & Async Python
- RAG Implementation
- Database Design
- Security Best Practices
- Docker & DevOps
- API Design
- Documentation

---

## 🙏 Acknowledgments

- FastAPI for the excellent framework
- OpenAI for AI capabilities
- FAISS for vector similarity search
- The open-source community

---

**Built with ❤️ and ☕ for technical excellence**
