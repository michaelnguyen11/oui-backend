# RAG Logic Architecture

This document describes the architecture and workflow of the Retrieval-Augmented Generation (RAG) system within the `oui-backend`, primarily located in the `open_webui/retrieval/` directory and orchestrated by `open_webui/routers/retrieval.py`.

## Core Components

1.  **Configuration (`open_webui/config.py`, `routers/retrieval.py`):**
    *   Defines crucial parameters for the RAG pipeline:
        *   Vector database type (`VECTOR_DB`).
        *   Embedding engine and model (`RAG_EMBEDDING_ENGINE`, `RAG_EMBEDDING_MODEL`).
        *   Reranking model (`RAG_RERANKING_MODEL`).
        *   Text splitting parameters (`CHUNK_SIZE`, `CHUNK_OVERLAP`, `RAG_TEXT_SPLITTER`).
        *   Retrieval parameters (`RAG_TOP_K`, `RAG_RELEVANCE_THRESHOLD`).
        *   Document loading engine (`CONTENT_EXTRACTION_ENGINE` - e.g., 'default', 'tika', 'document_intelligence').
        *   Web search engine settings and API keys.
    *   Configuration values are loaded into `app.state` and accessed throughout the RAG modules.
    *   Admin endpoints in `routers/retrieval.py` allow viewing and updating some of these settings.

2.  **Vector Database Abstraction (`open_webui/retrieval/vector/`):**
    *   `connector.py`: Acts as a factory, selecting the appropriate vector database client based on the `VECTOR_DB` config value.
    *   `dbs/`: Contains specific client implementations for supported databases (Chroma, Milvus, Qdrant, OpenSearch, Pgvector, Elasticsearch).
    *   `VECTOR_DB_CLIENT`: The instantiated client object, providing a consistent interface for adding, searching, getting, and deleting data in the chosen vector store. Used by `retrieval/utils.py`.

3.  **Document Loading (`open_webui/retrieval/loaders/`):**
    *   `main.py`: Defines the central `Loader` class.
    *   It selects a document loading strategy based on file type (`.pdf`, `.docx`, `.md`, etc.), content type, and the configured `CONTENT_EXTRACTION_ENGINE`.
    *   Leverages various `langchain_community.document_loaders` (e.g., `PyPDFLoader`, `Docx2txtLoader`, `TextLoader`) for standard file types.
    *   Can optionally use external services like Apache Tika (`TikaLoader`) or Azure AI Document Intelligence (`AzureAIDocumentIntelligenceLoader`) via configuration.
    *   Applies text cleaning using `ftfy.fix_text`.
    *   Specific loaders like `youtube.py` handle non-file sources.

4.  **Core Retrieval Utilities (`open_webui/retrieval/utils.py`):**
    *   Contains functions for embedding generation (`generate_embeddings`, `get_embedding_function`) supporting different engines (local SentenceTransformers, OpenAI, Ollama).
    *   Provides functions for querying the vector store (`query_doc`, `query_collection`) using `VECTOR_DB_CLIENT`.
    *   Implements hybrid search (`query_doc_with_hybrid_search`, `query_collection_with_hybrid_search`) using LangChain's `EnsembleRetriever` (combining vector search and `BM25Retriever`).
    *   Integrates reranking using LangChain's `ContextualCompressionRetriever` with a custom compressor (likely wrapping a `sentence_transformers.CrossEncoder` or custom models like ColBERT).
    *   Includes helpers for model downloading (`get_model_path`) and result processing (merging, sorting, deduplication).

5.  **Web Search Integration (`open_webui/retrieval/web/`):**
    *   Contains modules (`google_pse.py`, `bing.py`, `tavily.py`, etc.) for querying various configured web search engines.
    *   Results are processed into a standard format (`SearchResult`).
    *   Web content can be fetched using loaders (`get_web_loader`).

6.  **API Orchestration (`open_webui/routers/retrieval.py`):**
    *   Defines the API endpoints (`/api/v1/retrieval/...`).
    *   `/process/*` endpoints orchestrate the ingestion pipeline.
    *   `/query/*` endpoints orchestrate the querying pipeline.
    *   `/config/*`, `/embedding/*`, `/reranking/*` endpoints manage RAG configuration.
    *   `/delete`, `/reset/*` endpoints manage data within the RAG system.

## Workflows

### Ingestion Pipeline (e.g., File Upload via `/process/file`)

1.  File is uploaded via the API endpoint.
2.  The `Loader` (`loaders/main.py`) selects the appropriate mechanism to load the file content into LangChain `Document` objects.
3.  Text splitters (`RecursiveCharacterTextSplitter` or `TokenTextSplitter`) divide the documents into chunks based on configuration (`CHUNK_SIZE`, `CHUNK_OVERLAP`).
4.  Embeddings are generated for each chunk using the configured embedding function (`retrieval/utils.py`).
5.  The chunks (content, metadata, embeddings) are added to the specified collection in the vector database using `VECTOR_DB_CLIENT.add()`.

### Querying Pipeline (e.g., `/query/collection`)

1.  A query string is received by the API endpoint.
2.  An embedding is generated for the query string.
3.  The appropriate query function (`query_collection` or `query_collection_with_hybrid_search`) from `retrieval/utils.py` is called.
4.  **Vector Search:** `VECTOR_DB_CLIENT.search()` retrieves documents based on vector similarity.
5.  **(Optional) Hybrid Search:** BM25 keyword search is performed, results are combined with vector search results using `EnsembleRetriever`.
6.  **(Optional) Reranking:** The combined results are passed to a `ContextualCompressionRetriever` which uses a reranking model (CrossEncoder) to score and filter the documents based on relevance to the original query.
7.  The final list of relevant document chunks (content and metadata) is returned.

### Web Search RAG

1.  A query is sent to the `/process/web/search` endpoint (or web search is triggered within a chat flow).
2.  The configured search engine module in `retrieval/web/` is called to get search results.
3.  Optionally, content from result URLs is fetched using web loaders.
4.  This content can be directly used as context or potentially processed through the ingestion pipeline to be added to a vector collection for later retrieval.

## Summary

The RAG system is a modular component leveraging LangChain and various external services. It abstracts the vector database interaction, provides flexible document loading, generates embeddings, performs hybrid search and reranking, and integrates web search capabilities to provide relevant context for Large Language Models. Configuration plays a key role in tailoring the pipeline's behavior. 