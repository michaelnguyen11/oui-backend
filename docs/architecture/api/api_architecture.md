# API Architecture Documentation

This document provides a comprehensive overview of the API architecture, including class diagrams and sequence diagrams for key operations.

## Class Diagram

```mermaid
classDiagram
    class FastAPI {
        +include_router()
        +get_application()
    }

    class APIRouter {
        +get()
        +post()
        +put()
        +delete()
    }

    class BaseModel {
        +dict()
        +json()
    }

    class Request {
        +app
        +state
        +headers
        +cookies
    }

    class Response {
        +status_code
        +headers
        +body
    }

    class UserModel {
        +id: str
        +role: str
        +api_key: str
    }

    class AuthDependency {
        +get_verified_user()
        +get_admin_user()
        +get_current_user()
    }

    class ErrorHandler {
        +HTTPException
        +ValidationError
    }

    FastAPI --> APIRouter : contains
    APIRouter --> Request : handles
    APIRouter --> Response : returns
    APIRouter --> BaseModel : validates
    APIRouter --> AuthDependency : uses
    APIRouter --> ErrorHandler : handles
    AuthDependency --> UserModel : manages
```

## Router Class Diagram

```mermaid
classDiagram
    class BaseRouter {
        +router: APIRouter
        +get_verified_user()
        +get_admin_user()
    }

    class ChatRouter {
        +create_chat()
        +get_chat()
        +update_chat()
        +delete_chat()
    }

    class AuthRouter {
        +login()
        +register()
        +logout()
        +generate_api_key()
    }

    class RetrievalRouter {
        +process_file()
        +query_doc()
        +update_config()
    }

    class ModelRouter {
        +get_models()
        +update_model()
        +delete_model()
    }

    BaseRouter <|-- ChatRouter
    BaseRouter <|-- AuthRouter
    BaseRouter <|-- RetrievalRouter
    BaseRouter <|-- ModelRouter
```

## Sequence Diagrams

### 1. Chat Creation Flow

```mermaid
sequenceDiagram
    participant Client
    participant ChatRouter
    participant AuthDependency
    participant ChatService
    participant Database

    Client->>ChatRouter: POST /api/v1/chats/new
    ChatRouter->>AuthDependency: get_verified_user()
    AuthDependency-->>ChatRouter: UserModel
    ChatRouter->>ChatService: create_chat(user_id, data)
    ChatService->>Database: insert_chat()
    Database-->>ChatService: ChatModel
    ChatService-->>ChatRouter: ChatResponse
    ChatRouter-->>Client: 200 OK
```

### 2. RAG Document Processing Flow

```mermaid
sequenceDiagram
    participant Client
    participant RetrievalRouter
    participant AuthDependency
    participant DocumentProcessor
    participant VectorDB
    participant EmbeddingService

    Client->>RetrievalRouter: POST /api/v1/retrieval/process/file
    RetrievalRouter->>AuthDependency: get_verified_user()
    AuthDependency-->>RetrievalRouter: UserModel
    RetrievalRouter->>DocumentProcessor: process_file(file)
    DocumentProcessor->>DocumentProcessor: extract_content()
    DocumentProcessor->>DocumentProcessor: chunk_text()
    DocumentProcessor->>EmbeddingService: generate_embeddings()
    EmbeddingService-->>DocumentProcessor: embeddings
    DocumentProcessor->>VectorDB: store_documents()
    VectorDB-->>DocumentProcessor: success
    DocumentProcessor-->>RetrievalRouter: ProcessResult
    RetrievalRouter-->>Client: 200 OK
```

### 3. Model Configuration Update Flow

```mermaid
sequenceDiagram
    participant Client
    participant ModelRouter
    participant AuthDependency
    participant ConfigService
    participant Database

    Client->>ModelRouter: POST /api/v1/models/config
    ModelRouter->>AuthDependency: get_admin_user()
    AuthDependency-->>ModelRouter: UserModel
    ModelRouter->>ConfigService: update_model_config()
    ConfigService->>Database: update_config()
    Database-->>ConfigService: success
    ConfigService-->>ModelRouter: ConfigResponse
    ModelRouter-->>Client: 200 OK
```

## Component Details

### 1. Core Components

#### FastAPI Application
- Main application instance
- Router registration
- Middleware configuration
- Error handling

#### APIRouter
- Route registration
- Request handling
- Response formatting
- Dependency injection

#### Base Models
- Request validation
- Response serialization
- Data transfer objects

### 2. Authentication & Authorization

#### AuthDependency
- User verification
- Role-based access control
- API key management
- Session handling

#### UserModel
- User data structure
- Role management
- API key storage
- Permissions

### 3. Error Handling

#### HTTPException
- Status code mapping
- Error message formatting
- Response structure

#### ValidationError
- Input validation
- Schema validation
- Error reporting

## Best Practices

1. **Router Organization**
   - Group related endpoints
   - Use consistent naming
   - Implement proper versioning

2. **Authentication**
   - Always verify user identity
   - Implement role-based access
   - Secure API key handling

3. **Error Handling**
   - Consistent error responses
   - Proper status codes
   - Detailed error messages

4. **Performance**
   - Efficient database queries
   - Proper caching
   - Async operations

5. **Security**
   - Input validation
   - Output sanitization
   - Rate limiting

6. **Documentation**
   - Clear endpoint descriptions
   - Request/response examples
   - Error scenarios 