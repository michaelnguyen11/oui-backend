# Development Guidelines

This document provides comprehensive guidelines for developing and contributing to the Open WebUI backend.

## Development Setup

### 1. Environment Setup

#### Prerequisites
```bash
# Required tools
python >= 3.8
pip >= 21.0
git
docker (optional)
```

#### Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Unix
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. IDE Configuration

#### VS Code Settings
```json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

#### PyCharm Settings
- Enable Black formatter
- Configure pylint
- Set up pytest
- Enable type checking

## Code Style

### 1. Python Style Guide

#### General Rules
- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for all public functions
- Keep functions focused and small
- Use meaningful variable names

#### Example
```python
from typing import List, Optional

def process_documents(
    documents: List[str],
    chunk_size: int = 1000,
    chunk_overlap: Optional[int] = None
) -> List[str]:
    """
    Process a list of documents and split them into chunks.

    Args:
        documents: List of document strings to process
        chunk_size: Size of each chunk in characters
        chunk_overlap: Number of characters to overlap between chunks

    Returns:
        List of processed document chunks

    Raises:
        ValueError: If chunk_size is less than 1
    """
    if chunk_size < 1:
        raise ValueError("chunk_size must be greater than 0")
    
    # Implementation
    return processed_chunks
```

### 2. Project Structure

```
open_webui/
├── __init__.py
├── config.py
├── main.py
├── routers/
│   ├── __init__.py
│   ├── chat.py
│   ├── retrieval.py
│   └── admin.py
├── models/
│   ├── __init__.py
│   ├── chat.py
│   └── retrieval.py
├── services/
│   ├── __init__.py
│   ├── chat.py
│   └── retrieval.py
├── utils/
│   ├── __init__.py
│   ├── auth.py
│   └── validation.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_chat.py
    └── test_retrieval.py
```

## Testing

### 1. Unit Testing

#### Test Structure
```python
import pytest
from open_webui.services.retrieval import process_document

def test_process_document():
    # Arrange
    document = "Test document content"
    chunk_size = 5
    
    # Act
    result = process_document(document, chunk_size)
    
    # Assert
    assert len(result) == 4
    assert all(len(chunk) <= chunk_size for chunk in result)
```

#### Test Coverage
```bash
# Run tests with coverage
pytest --cov=open_webui tests/

# Generate coverage report
pytest --cov=open_webui --cov-report=html tests/
```

### 2. Integration Testing

#### API Testing
```python
from fastapi.testclient import TestClient
from open_webui.main import app

client = TestClient(app)

def test_chat_endpoint():
    response = client.post(
        "/api/chat/completions",
        json={
            "model": "test-model",
            "messages": [{"role": "user", "content": "Hello"}]
        }
    )
    assert response.status_code == 200
    assert "choices" in response.json()
```

#### Database Testing
```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
```

## Documentation

### 1. Code Documentation

#### Function Documentation
```python
def generate_embeddings(
    text: str,
    model: str = "sentence-transformers/all-MiniLM-L6-v2"
) -> List[float]:
    """
    Generate embeddings for the given text using the specified model.

    Args:
        text: Input text to generate embeddings for
        model: Name of the model to use for embedding generation

    Returns:
        List of embedding values

    Raises:
        ValueError: If text is empty
        ModelNotFoundError: If specified model is not available
    """
```

#### Class Documentation
```python
class VectorDBClient:
    """
    Client for interacting with vector database.

    This class provides a unified interface for various vector database
    implementations, handling connection management and query execution.

    Attributes:
        connection: Database connection object
        pool_size: Size of the connection pool
    """
```

### 2. API Documentation

#### OpenAPI Schema
```python
from pydantic import BaseModel

class ChatMessage(BaseModel):
    """
    Schema for chat messages.

    Attributes:
        role: Role of the message sender (user/assistant)
        content: Content of the message
    """
    role: str
    content: str

    class Config:
        schema_extra = {
            "example": {
                "role": "user",
                "content": "Hello, how are you?"
            }
        }
```

## Version Control

### 1. Git Workflow

#### Branch Naming
- feature/feature-name
- bugfix/bug-description
- hotfix/issue-description
- release/version-number

#### Commit Messages
```
feat: add support for custom embedding models

- Add configuration for custom model selection
- Implement model loading and validation
- Add tests for custom model support

Closes #123
```

### 2. Pull Request Guidelines

#### PR Template
```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Tests passing
- [ ] No new warnings
```

## Performance Optimization

### 1. Code Optimization

#### Caching
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_embedding_function(model: str) -> Callable:
    """Cache embedding function instances."""
    return load_model(model)
```

#### Async Operations
```python
async def process_documents_parallel(documents: List[str]) -> List[str]:
    """Process multiple documents in parallel."""
    tasks = [process_document(doc) for doc in documents]
    return await asyncio.gather(*tasks)
```

### 2. Database Optimization

#### Query Optimization
```python
# Use select_from for better performance
result = (
    db.query(Model)
    .select_from(Model)
    .filter(Model.status == "active")
    .limit(100)
    .all()
)
```

#### Indexing
```python
class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True)
    content = Column(Text, index=True)  # Add index for frequent searches
```

## Security

### 1. Input Validation

#### Data Validation
```python
from pydantic import BaseModel, validator

class UserInput(BaseModel):
    content: str
    
    @validator("content")
    def validate_content(cls, v):
        if len(v) > 10000:
            raise ValueError("Content too long")
        return v
```

#### SQL Injection Prevention
```python
# Use parameterized queries
result = db.execute(
    "SELECT * FROM documents WHERE id = :id",
    {"id": document_id}
)
```

### 2. Authentication

#### Token Validation
```python
async def validate_token(token: str) -> bool:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return True
    except jwt.InvalidTokenError:
        return False
```

## Deployment

### 1. Docker Configuration

#### Dockerfile
```dockerfile
FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "open_webui.main:app", "--host", "0.0.0.0", "--port", "3000"]
```

#### Docker Compose
```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "3000:3000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - VECTOR_DB=chroma
    volumes:
      - ./data:/app/data
```

### 2. CI/CD Pipeline

#### GitHub Actions
```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    - name: Run tests
      run: |
        pytest --cov=open_webui tests/
```

## Best Practices

1. **Code Quality**
   - Follow PEP 8 guidelines
   - Write comprehensive tests
   - Maintain good documentation
   - Use type hints

2. **Performance**
   - Optimize database queries
   - Implement caching
   - Use async operations
   - Monitor resource usage

3. **Security**
   - Validate all inputs
   - Use parameterized queries
   - Implement proper authentication
   - Follow security best practices

4. **Maintenance**
   - Keep dependencies updated
   - Monitor error logs
   - Regular code reviews
   - Documentation updates

5. **Collaboration**
   - Follow git workflow
   - Write clear commit messages
   - Provide detailed PR descriptions
   - Respond to code reviews 