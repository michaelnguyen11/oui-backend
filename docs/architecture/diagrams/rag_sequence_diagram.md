# RAG System Sequence Diagrams

This document provides detailed sequence diagrams for the RAG (Retrieval-Augmented Generation) system's key operations.

## 1. Document Ingestion Flow

```mermaid
sequenceDiagram
    participant Client
    participant RetrievalRouter
    participant DocumentLoader
    participant TextSplitter
    participant EmbeddingService
    participant VectorDB
    participant ConfigService

    Client->>RetrievalRouter: POST /api/v1/retrieval/process/file
    RetrievalRouter->>ConfigService: get_rag_config()
    ConfigService-->>RetrievalRouter: RAGConfig
    
    RetrievalRouter->>DocumentLoader: load_document(file)
    DocumentLoader->>DocumentLoader: detect_file_type()
    DocumentLoader->>DocumentLoader: extract_content()
    DocumentLoader-->>RetrievalRouter: Document
    
    RetrievalRouter->>TextSplitter: split_text(document)
    TextSplitter->>TextSplitter: chunk_text()
    TextSplitter-->>RetrievalRouter: Chunks[]
    
    RetrievalRouter->>EmbeddingService: generate_embeddings(chunks)
    EmbeddingService->>EmbeddingService: select_embedding_model()
    EmbeddingService->>EmbeddingService: batch_process()
    EmbeddingService-->>RetrievalRouter: Embeddings[]
    
    RetrievalRouter->>VectorDB: store_documents(chunks, embeddings)
    VectorDB->>VectorDB: validate_vectors()
    VectorDB->>VectorDB: index_documents()
    VectorDB-->>RetrievalRouter: Success
    
    RetrievalRouter-->>Client: 200 OK
```

## 2. Query Processing Flow

```mermaid
sequenceDiagram
    participant Client
    participant RetrievalRouter
    participant EmbeddingService
    participant VectorDB
    participant RerankingService
    participant LLMService

    Client->>RetrievalRouter: POST /api/v1/retrieval/query/collection
    RetrievalRouter->>EmbeddingService: generate_query_embedding(query)
    EmbeddingService-->>RetrievalRouter: QueryEmbedding
    
    RetrievalRouter->>VectorDB: search_documents(query_embedding)
    VectorDB->>VectorDB: vector_search()
    VectorDB-->>RetrievalRouter: CandidateDocuments[]
    
    alt Hybrid Search Enabled
        RetrievalRouter->>VectorDB: bm25_search(query)
        VectorDB-->>RetrievalRouter: BM25Results[]
        RetrievalRouter->>RetrievalRouter: merge_results()
    end
    
    RetrievalRouter->>RerankingService: rerank_documents(documents)
    RerankingService->>RerankingService: cross_encoder_rerank()
    RerankingService-->>RetrievalRouter: RerankedDocuments[]
    
    RetrievalRouter->>LLMService: generate_response(query, documents)
    LLMService->>LLMService: format_prompt()
    LLMService->>LLMService: generate_completion()
    LLMService-->>RetrievalRouter: Response
    
    RetrievalRouter-->>Client: 200 OK
```

## 3. Web Search Integration Flow

```mermaid
sequenceDiagram
    participant Client
    participant RetrievalRouter
    participant WebSearchService
    participant DocumentLoader
    participant EmbeddingService
    participant VectorDB

    Client->>RetrievalRouter: POST /api/v1/retrieval/process/web/search
    RetrievalRouter->>WebSearchService: search_web(query)
    WebSearchService->>WebSearchService: execute_search()
    WebSearchService-->>RetrievalRouter: SearchResults[]
    
    loop For each result
        RetrievalRouter->>DocumentLoader: load_web_content(url)
        DocumentLoader->>DocumentLoader: fetch_content()
        DocumentLoader->>DocumentLoader: extract_text()
        DocumentLoader-->>RetrievalRouter: WebDocument
        
        RetrievalRouter->>EmbeddingService: generate_embeddings(document)
        EmbeddingService-->>RetrievalRouter: Embeddings[]
        
        RetrievalRouter->>VectorDB: store_document(document, embeddings)
        VectorDB-->>RetrievalRouter: Success
    end
    
    RetrievalRouter-->>Client: 200 OK
```

## 4. Configuration Update Flow

```mermaid
sequenceDiagram
    participant Client
    participant RetrievalRouter
    participant ConfigService
    participant EmbeddingService
    participant RerankingService
    participant VectorDB

    Client->>RetrievalRouter: POST /api/v1/retrieval/config/update
    RetrievalRouter->>ConfigService: validate_config(config)
    ConfigService-->>RetrievalRouter: ValidatedConfig
    
    alt Embedding Model Update
        RetrievalRouter->>EmbeddingService: update_embedding_model(config)
        EmbeddingService->>EmbeddingService: download_model()
        EmbeddingService->>EmbeddingService: initialize_model()
        EmbeddingService-->>RetrievalRouter: Success
    end
    
    alt Reranking Model Update
        RetrievalRouter->>RerankingService: update_reranking_model(config)
        RerankingService->>RerankingService: download_model()
        RerankingService->>RerankingService: initialize_model()
        RerankingService-->>RetrievalRouter: Success
    end
    
    RetrievalRouter->>VectorDB: update_vector_config(config)
    VectorDB-->>RetrievalRouter: Success
    
    RetrievalRouter-->>Client: 200 OK
```

## Component Interactions

### 1. Document Processing
- File type detection
- Content extraction
- Text chunking
- Embedding generation
- Vector storage

### 2. Query Processing
- Query embedding
- Vector search
- Hybrid search (optional)
- Reranking
- Response generation

### 3. Web Search
- Search execution
- Content fetching
- Text extraction
- Document processing
- Vector storage

### 4. Configuration Management
- Model updates
- Parameter validation
- Service reinitialization
- Vector store configuration

## Error Handling

1. **Document Processing Errors**
   - File type unsupported
   - Content extraction failed
   - Chunking errors
   - Embedding generation failed

2. **Query Processing Errors**
   - Invalid query
   - Search failed
   - Reranking errors
   - Response generation failed

3. **Web Search Errors**
   - Search API errors
   - Content fetch failed
   - Processing errors
   - Storage errors

4. **Configuration Errors**
   - Invalid parameters
   - Model download failed
   - Initialization errors
   - Storage configuration errors 