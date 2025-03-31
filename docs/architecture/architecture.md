# Oui-Backend High-Level Architecture

This document provides a high-level overview of the `oui-backend` application architecture.

## Core Components

1.  **Client Interface (External):**
    *   Likely a web browser or other HTTP/WebSocket client.
    *   Interacts with the backend via HTTP requests and WebSocket connections.

2.  **Web Server (FastAPI):**
    *   The core of the backend, built using the FastAPI framework.
    *   Receives incoming connections and requests.
    *   Handles routing to appropriate API logic based on URL paths.
    *   Manages middleware for cross-cutting concerns (e.g., authentication, CORS, logging).
    *   Serves static frontend assets located in `open_webui/static/`.
    *   Primary implementation: `open_webui/main.py`.

3.  **API Routers (`open_webui/routers/`):**
    *   Modular components containing the business logic for specific API endpoint groups.
    *   Examples: `/chats`, `/models`, `/users`, `/retrieval`.
    *   Process request data, interact with other components, and formulate responses.

4.  **Database Layer:**
    *   **ORM (SQLAlchemy):** Maps Python objects to database tables (`open_webui/models/`). Manages database sessions and queries.
    *   **Migrations (Alembic):** Handles database schema evolution (`open_webui/migrations/`, `alembic.ini`).
    *   **Database (External):** The persistent relational database storing application state.

5.  **Real-time Layer (`open_webui/socket/`):**
    *   Manages WebSocket connections for bidirectional, real-time communication between the server and connected clients (e.g., for chat updates, notifications).

6.  **RAG & AI Logic:**
    *   **Retrieval Module (`open_webui/retrieval/`):** Implements Retrieval-Augmented Generation (RAG) functionality. This includes document loading, text splitting, embedding generation, vector storage/search, and context formulation.
    *   **LLM Integration (`routers/ollama.py`, `routers/openai.py`, etc.):** Handles communication protocols and interactions with configured Large Language Models (LLMs).
    *   **Other AI Features:** Dedicated modules/routers for specific AI capabilities like image generation (`routers/images.py`), audio processing (`routers/audio.py`), and tool/function execution (`routers/functions.py`, `routers/tools.py`).

7.  **Configuration (`open_webui/config.py`):**
    *   Loads and provides centralized access to application settings, credentials, API keys, and feature flags, often sourced from environment variables or configuration files.

8.  **Background Tasks (`open_webui/tasks.py` & FastAPI Integration):**
    *   Handles asynchronous or long-running operations offloaded from the main request-response cycle (e.g., processing uploads, running complex computations).

9.  **Utilities (`open_webui/utils/`):**
    *   A collection of shared helper functions, constants, logging configurations, and other common code used across the application.

## Key Interactions Flow (Example: New Chat Message)

1.  **Client** sends a POST request to `/chats/{chat_id}/message` with the message content.
2.  **Web Server (FastAPI)** receives the request and routes it to the appropriate function in `routers/chats.py`.
3.  The **Chat Router** function:
    *   Validates the incoming message data.
    *   Authenticates the user (likely via middleware).
    *   May interact with the **Database Layer** to retrieve chat history or user details.
    *   Optionally calls the **RAG Module** to fetch relevant context from documents based on the message.
    *   Constructs a prompt including the message and potentially retrieved context.
    *   Sends the prompt to the configured **LLM Integration** module.
    *   Receives the LLM response.
    *   Saves the new message and response to the **Database Layer**.
    *   May send real-time updates to connected clients via the **Real-time Layer (WebSockets)**.
    *   Returns the response to the originating **Client**.

This flow illustrates how different components collaborate to fulfill a user request, orchestrated by the FastAPI server and API routers. Configuration settings influence which external services (database, LLMs, etc.) are used. 