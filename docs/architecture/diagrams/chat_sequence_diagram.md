# Chat Processing Sequence Diagrams

This document provides detailed sequence diagrams for the chat processing system's key operations.

## 1. Chat Creation Flow

```mermaid
sequenceDiagram
    participant Client
    participant ChatRouter
    participant ChatService
    participant ModelService
    participant Database
    participant Cache

    Client->>ChatRouter: POST /api/v1/chats/new
    ChatRouter->>ChatService: create_chat()
    ChatService->>ModelService: get_model_config()
    ModelService-->>ChatService: ModelConfig
    
    ChatService->>Database: create_chat_record()
    Database-->>ChatService: ChatRecord
    
    ChatService->>Cache: initialize_chat_context()
    Cache-->>ChatService: ContextCreated
    
    ChatService-->>ChatRouter: ChatResponse
    ChatRouter-->>Client: 200 OK
```

## 2. Message Processing Flow

```mermaid
sequenceDiagram
    participant Client
    participant ChatRouter
    participant ChatService
    participant ModelService
    participant RAGService
    participant Database
    participant Cache

    Client->>ChatRouter: POST /api/v1/chats/{chat_id}/message
    ChatRouter->>ChatService: process_message()
    ChatService->>Cache: get_chat_context()
    Cache-->>ChatService: ChatContext
    
    alt RAG Enabled
        ChatService->>RAGService: retrieve_relevant_context()
        RAGService->>RAGService: search_documents()
        RAGService-->>ChatService: RelevantContext
    end
    
    ChatService->>ModelService: generate_response()
    ModelService->>ModelService: format_prompt()
    ModelService->>ModelService: generate_completion()
    ModelService-->>ChatService: Response
    
    ChatService->>Database: store_message()
    Database-->>ChatService: MessageRecord
    
    ChatService->>Cache: update_chat_context()
    Cache-->>ChatService: ContextUpdated
    
    ChatService-->>ChatRouter: MessageResponse
    ChatRouter-->>Client: 200 OK
```

## 3. Streaming Response Flow

```mermaid
sequenceDiagram
    participant Client
    participant ChatRouter
    participant ChatService
    participant ModelService
    participant RAGService
    participant Cache

    Client->>ChatRouter: POST /api/v1/chats/{chat_id}/stream
    ChatRouter->>ChatService: process_streaming_message()
    ChatService->>Cache: get_chat_context()
    Cache-->>ChatService: ChatContext
    
    alt RAG Enabled
        ChatService->>RAGService: retrieve_relevant_context()
        RAGService-->>ChatService: RelevantContext
    end
    
    ChatService->>ModelService: generate_streaming_response()
    ModelService->>ModelService: format_prompt()
    
    loop For each token
        ModelService->>ModelService: generate_token()
        ModelService-->>ChatService: Token
        ChatService-->>ChatRouter: Token
        ChatRouter-->>Client: Token
    end
    
    ChatService->>Database: store_complete_message()
    Database-->>ChatService: MessageRecord
    
    ChatService->>Cache: update_chat_context()
    Cache-->>ChatService: ContextUpdated
```

## 4. Chat History Management Flow

```mermaid
sequenceDiagram
    participant Client
    participant ChatRouter
    participant ChatService
    participant Database
    participant Cache
    participant ExportService

    Client->>ChatRouter: GET /api/v1/chats/{chat_id}/history
    ChatRouter->>ChatService: get_chat_history()
    ChatService->>Cache: get_cached_history()
    
    alt Cache Miss
        Cache-->>ChatService: CacheMiss
        ChatService->>Database: fetch_chat_history()
        Database-->>ChatService: ChatHistory
        ChatService->>Cache: cache_history()
    else Cache Hit
        Cache-->>ChatService: ChatHistory
    end
    
    ChatService-->>ChatRouter: HistoryResponse
    ChatRouter-->>Client: 200 OK
```

## Component Interactions

### 1. Chat Management
- Chat creation
- Context initialization
- History tracking
- State management

### 2. Message Processing
- Context retrieval
- RAG integration
- Model interaction
- Response generation

### 3. Streaming
- Token generation
- Real-time updates
- Context maintenance
- State persistence

### 4. History Management
- History retrieval
- Caching
- Export functionality
- State restoration

## Error Handling

1. **Chat Creation Errors**
   - Invalid configuration
   - Resource constraints
   - Context initialization failed
   - Database errors

2. **Message Processing Errors**
   - Context retrieval failed
   - RAG search failed
   - Model errors
   - Response generation failed

3. **Streaming Errors**
   - Connection issues
   - Token generation failed
   - State corruption
   - Timeout errors

4. **History Management Errors**
   - Cache errors
   - Database errors
   - Export failures
   - State restoration failed 