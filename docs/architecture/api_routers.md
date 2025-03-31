# API Routers Architecture

This document outlines the structure and purpose of the API routers used in the `oui-backend` application, located primarily within the `open_webui/routers/` directory.

## General Structure

The API is built using FastAPI's `APIRouter`. Each Python file typically represents a logical grouping of related endpoints.

The common structure within each router file (`e.g., open_webui/routers/chats.py`) is:

1.  **Imports:** Necessary components are imported, including:
    *   FastAPI elements (`APIRouter`, `Depends`, `HTTPException`, `Request`).
    *   Pydantic models (`BaseModel` subclasses) for request bodies and response validation.
    *   SQLAlchemy models and data access classes (e.g., `Chats`, `UsersTable`) from `open_webui/models/`.
    *   Authentication utilities (`get_verified_user`, `get_admin_user`) from `open_webui/utils/auth.py`.
    *   Other utility functions, constants, and configuration values.
2.  **Router Instantiation:** An `APIRouter` instance is created: `router = APIRouter()`.
3.  **Path Operations (Endpoints):** Functions are defined and decorated with `@router.get`, `@router.post`, `@router.put`, `@router.delete`, etc., to handle specific HTTP methods and URL paths relative to the router's prefix.
4.  **Request/Response Modeling:** Pydantic models define the expected structure of request bodies (`form_data: ChatForm`) and are used in `response_model` decorators to specify and validate the response format.
5.  **Dependency Injection (`Depends`):** FastAPI's dependency injection is used to:
    *   Ensure user authentication and authorization by depending on functions like `get_verified_user` or `get_admin_user`.
    *   Potentially inject other shared resources or configurations.
6.  **Logic Execution:** Endpoint functions orchestrate the required actions:
    *   Validate inputs and user permissions.
    *   Interact with the database by calling methods on data access layer classes.
    *   Call other services or utility functions (e.g., LLM interaction, RAG pipeline).
    *   Handle errors using `HTTPException`.
    *   Return appropriate responses, often serialized using Pydantic `response_model`s.

## Router File Purposes

Based on filenames and analysis, here's a summary of the purpose of each router file found in `open_webui/routers/`:

*   **`audio.py`:** Handles audio processing endpoints (e.g., Speech-to-Text, Text-to-Speech).
*   **`auths.py`:** Manages user authentication (signin, signup, signout), profile/password updates, API key generation/management, LDAP integration, and some admin configuration endpoints.
*   **`channels.py`:** Likely manages different communication channels or contexts within the application.
*   **`chats.py`:** Core chat functionality including CRUD operations, searching, importing, archiving, sharing, and tagging chats.
*   **`configs.py`:** Provides endpoints for fetching and potentially modifying application-wide configurations (likely restricted to admins).
*   **`evaluations.py`:** Contains endpoints related to model evaluations or comparisons (e.g., arena mode).
*   **`files.py`:** Manages metadata and potentially storage of user-uploaded files (distinct from RAG document handling).
*   **`folders.py`:** Provides endpoints for creating, managing, and organizing chats or other items into folders.
*   **`functions.py`:** Manages definitions of functions that LLMs can utilize (part of function calling/tool use).
*   **`groups.py`:** Handles endpoints related to user groups or possibly grouping chats.
*   **`images.py`:** Contains endpoints for interacting with image generation models/services.
*   **`knowledge.py`:** Manages knowledge bases or document collections, likely interacting with the RAG system.
*   **`memories.py`:** Endpoints related to managing conversation memory or context summaries for LLMs.
*   **`models.py`:** Provides endpoints to list, fetch details of, update, or pull available LLM models configured in the backend.
*   **`ollama.py`:** Contains specific endpoints for direct interaction with an Ollama backend API (proxying or extending).
*   **`openai.py`:** Contains specific endpoints for direct interaction with an OpenAI-compatible API (proxying or extending).
*   **`pipelines.py`:** Provides endpoints for defining, executing, or managing complex, multi-step workflows or pipelines.
*   **`prompts.py`:** Manages user-saved prompts or prompt templates.
*   **`retrieval.py`:** The core of the RAG system. Handles configuration (embedding, reranking, chunking, web search), data ingestion from various sources (files, URLs, text) into vector stores, querying those stores, and managing RAG data.
*   **`tasks.py`:** Provides endpoints for listing, stopping, or monitoring background tasks.
*   **`tools.py`:** Manages definitions and potentially execution of tools that LLMs can use.
*   **`users.py`:** Contains admin-focused endpoints for managing users (listing, updating roles, deleting).
*   **`utils.py`:** Offers miscellaneous utility endpoints: Gravatar URLs, code formatting (`black`), code execution (via Jupyter), Markdown-to-HTML conversion, PDF generation for chats, and admin downloads (SQLite DB, LiteLLM config).

## Integration

These routers are included in the main FastAPI application (`open_webui/main.py`) using `app.include_router()`, typically with a prefix like `/api/v1/` or specific prefixes like `/ollama`. 