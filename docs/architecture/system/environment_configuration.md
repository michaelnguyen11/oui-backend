# Environment Configuration

This document details the environment variables and configuration options available in the Open WebUI backend.

## RAG Configuration

### Embedding Configuration

#### `RAG_EMBEDDING_ENGINE`
- **Type**: `str`
- **Default**: Empty string (uses SentenceTransformers)
- **Options**:
  - Empty string: Default (SentenceTransformers)
  - `ollama`: Uses the Ollama API
  - `openai`: Uses the OpenAI API
- **Description**: Selects the embedding engine for RAG
- **Persistence**: `PersistentConfig` variable

#### `RAG_EMBEDDING_MODEL`
- **Type**: `str`
- **Default**: `sentence-transformers/all-MiniLM-L6-v2`
- **Description**: Sets the model for embeddings
- **Persistence**: `PersistentConfig` variable

#### `RAG_EMBEDDING_BATCH_SIZE`
- **Type**: `int`
- **Default**: `1`
- **Description**: Sets the batch size for embedding generation
- **Persistence**: `PersistentConfig` variable

### Search Configuration

#### `ENABLE_RAG_HYBRID_SEARCH`
- **Type**: `bool`
- **Default**: `False`
- **Description**: Enables ensemble search with BM25 + ChromaDB, with reranking using sentence_transformers models
- **Persistence**: `PersistentConfig` variable

#### `RAG_TOP_K`
- **Type**: `int`
- **Default**: `3`
- **Description**: Sets the default number of results to consider for embedding
- **Persistence**: `PersistentConfig` variable

#### `RAG_RELEVANCE_THRESHOLD`
- **Type**: `float`
- **Default**: `0.0`
- **Description**: Sets the relevance threshold for document filtering with reranking
- **Persistence**: `PersistentConfig` variable

### Document Processing

#### `CONTENT_EXTRACTION_ENGINE`
- **Type**: `str`
- **Options**:
  - Empty string: Default
  - `tika`: Use local Apache Tika server
- **Description**: Sets the content extraction engine for document ingestion
- **Persistence**: `PersistentConfig` variable

#### `CHUNK_SIZE`
- **Type**: `int`
- **Default**: `1000`
- **Description**: Sets the document chunk size for embeddings
- **Persistence**: `PersistentConfig` variable

#### `CHUNK_OVERLAP`
- **Type**: `int`
- **Default**: `100`
- **Description**: Specifies overlap between chunks
- **Persistence**: `PersistentConfig` variable

### File Limits

#### `RAG_FILE_MAX_SIZE`
- **Type**: `int`
- **Description**: Maximum file size in MB for document ingestion
- **Persistence**: `PersistentConfig` variable

#### `RAG_FILE_MAX_COUNT`
- **Type**: `int`
- **Description**: Maximum number of files for document ingestion
- **Persistence**: `PersistentConfig` variable

:::info
When configuring `RAG_FILE_MAX_SIZE` and `RAG_FILE_MAX_COUNT`, ensure values are reasonable to prevent excessive uploads and performance issues.
:::

### Reranking Configuration

#### `RAG_RERANKING_MODEL`
- **Type**: `str`
- **Description**: Sets the model for reranking results
- **Persistence**: `PersistentConfig` variable

### API Configuration

#### `RAG_OPENAI_API_BASE_URL`
- **Type**: `str`
- **Default**: `${OPENAI_API_BASE_URL}`
- **Description**: OpenAI base API URL for RAG embeddings
- **Persistence**: `PersistentConfig` variable

#### `RAG_OPENAI_API_KEY`
- **Type**: `str`
- **Default**: `${OPENAI_API_KEY}`
- **Description**: OpenAI API key for RAG embeddings
- **Persistence**: `PersistentConfig` variable

#### `RAG_OLLAMA_BASE_URL`
- **Type**: `str`
- **Description**: Base URL for Ollama API in RAG models
- **Persistence**: `PersistentConfig` variable

#### `RAG_OLLAMA_API_KEY`
- **Type**: `str`
- **Description**: API key for Ollama API in RAG models
- **Persistence**: `PersistentConfig` variable

### Additional Features

#### `PDF_EXTRACT_IMAGES`
- **Type**: `bool`
- **Default**: `False`
- **Description**: Extract images from PDFs using OCR
- **Persistence**: `PersistentConfig` variable

#### `ENABLE_RAG_WEB_SEARCH`
- **Type**: `bool`
- **Description**: Enable web search functionality
- **Persistence**: `PersistentConfig` variable

#### `RAG_WEB_SEARCH_ENGINE`
- **Type**: `str`
- **Description**: Configure web search engine
- **Persistence**: `PersistentConfig` variable

## Usage Examples

### Basic RAG Setup

```bash
# Enable hybrid search
ENABLE_RAG_HYBRID_SEARCH=true

# Configure embedding model
RAG_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Set chunk size and overlap
CHUNK_SIZE=1000
CHUNK_OVERLAP=100

# Configure file limits
RAG_FILE_MAX_SIZE=10
RAG_FILE_MAX_COUNT=100
```

### OpenAI Integration

```bash
# Configure OpenAI for embeddings
RAG_EMBEDDING_ENGINE=openai
RAG_EMBEDDING_MODEL=text-embedding-ada-002
RAG_OPENAI_API_KEY=your-api-key
```

### Ollama Integration

```bash
# Configure Ollama for embeddings
RAG_EMBEDDING_ENGINE=ollama
RAG_OLLAMA_BASE_URL=http://localhost:11434
RAG_OLLAMA_API_KEY=your-api-key
```

## Best Practices

1. **Context Length**
   - For Ollama models, increase context length to 8192+ tokens
   - This ensures retrieved data fits within context window

2. **File Management**
   - Set reasonable limits for file size and count
   - Monitor system resources during document processing

3. **API Keys**
   - Store API keys securely
   - Use environment variables or secure secret management
   - Never commit API keys to version control

4. **Performance Tuning**
   - Adjust chunk size and overlap based on document types
   - Monitor embedding and retrieval performance
   - Fine-tune relevance thresholds as needed

5. **Security**
   - Enable SSL verification for web loaders
   - Restrict file types and sizes
   - Implement proper authentication and authorization 