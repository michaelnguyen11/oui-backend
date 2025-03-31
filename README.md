# oui-backend (Open WebUI Backend)

This repository contains the backend server for Open WebUI, a user-friendly and extensible interface for interacting with Large Language Models (LLMs).

## Overview

The backend is built using Python and the FastAPI framework. It provides a comprehensive API for managing users, chats, documents, models, and integrations with various AI services.

## Key Features

*   **FastAPI Framework:** Modern, fast (high-performance) web framework for building APIs.
*   **LLM Integration:** Supports connections to multiple LLM providers and backends (e.g., Ollama, OpenAI API compatible).
*   **Retrieval-Augmented Generation (RAG):** Enables interaction with documents and knowledge bases using vector embeddings and retrieval techniques.
*   **Database:** Uses SQLAlchemy for ORM and Alembic for database migrations.
*   **Real-time Communication:** Implements WebSockets for features requiring live updates.
*   **Modular Architecture:** API endpoints are organized into logical modules within the `open_webui/routers/` directory.
*   **Extensibility:** Designed to support various extensions like image generation, audio processing (STT/TTS), function/tool usage, and more.
*   **Configuration:** Highly configurable via environment variables and configuration files (`open_webui/config.py`).

## Architecture

The backend follows a standard web application architecture:

1.  **Entry Point (`open_webui/main.py`):** Initializes the FastAPI application, configures middleware (CORS, sessions, logging), and includes API routers.
2.  **API Routers (`open_webui/routers/`):** Define API endpoints grouped by functionality (e.g., `auths.py`, `chats.py`, `retrieval.py`).
3.  **Database Layer (`open_webui/models/`, `open_webui/internal/db.py`, `open_webui/migrations/`):** Manages data models (SQLAlchemy), database sessions, and schema migrations (Alembic).
4.  **Core Modules:**
    *   `open_webui/retrieval/`: Logic for RAG, embeddings, document parsing.
    *   `open_webui/socket/`: WebSocket handling.
    *   `open_webui/utils/`: Shared utilities and helpers.
    *   `open_webui/config.py`: Application configuration loading.
5.  **Static Files (`open_webui/static/`):** Serves frontend assets (though the primary frontend might reside in a separate repository or be built into this structure).
6.  **Data Storage (`data/`):** Likely used for persistent application data (e.g., uploaded files, vector stores).

## Getting Started

### Prerequisites

*   Python 3.x
*   Pip (Python package installer)

### Installation

1.  Clone the repository:
    ```bash
    git clone <repository-url>
    cd oui-backend
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Configure environment variables (refer to `.env.example` if available, or the configuration documentation). Key configurations might include database connection details, LLM API endpoints/keys, etc.

### Running the Application

*   **Linux/macOS:**
    ```bash
    ./start.sh
    ```
*   **Windows:**
    ```bash
    ./start_windows.bat
    ```
*   **Development:**
    ```bash
    ./dev.sh
    ```

This will typically start the FastAPI server (often using Uvicorn). You can then access the API, usually at `http://localhost:8080` (check the startup scripts or configuration for the exact host and port).

## Project Structure
├── data/ # Application data (e.g., uploaded files, DBs)
├── open_webui/ # Main application source code
│ ├── internal/ # Internal modules
│ ├── migrations/ # Alembic database migrations
│ ├── models/ # SQLAlchemy ORM models
│ ├── retrieval/ # RAG and document processing logic
│ ├── routers/ # API endpoint definitions
│ ├── socket/ # WebSocket handling
│ ├── static/ # Static files for frontend
│ ├── utils/ # Utility functions
│ ├── init.py
│ ├── alembic.ini # Alembic configuration
│ ├── config.py # Application configuration loading
│ ├── constants.py # Constant values
│ ├── env.py # Alembic environment setup
│ ├── functions.py # Core functions/logic
│ ├── main.py # FastAPI application entry point
│ └── tasks.py # Background task definitions
├── .git/ # Git version control
├── dev.sh # Development start script
├── README.md # This file
├── requirements.txt # Python dependencies
├── start.sh # Linux/macOS start script
└── start_windows.bat # Windows start script

## Documentation Structure (`docs/`)

This project includes detailed architecture documentation within the `docs/` folder to aid understanding. It is organized as follows:

*   **`docs/understanding_the_backend.md`**: A guided tour and recommended steps for new contributors to understand the codebase using the available documentation. **Start here!**
*   **`docs/architecture/`**: Contains markdown files describing the different architectural components and concepts:
    *   `architecture.md`: High-level system overview.
    *   Component-specific files (e.g., `web_server.md`, `database_layer.md`, `rag_logic.md`, `real_time_layer.md`, `api_routers.md`, `configuration.md`, `utilities.md`, etc.).
    *   Deeper dives into specific components (e.g., `deep_dive_api_routers.md`).
*   **`docs/diagrams/`**: Contains source files for architectural diagrams (using PlantUML). You can render these using PlantUML tools.
    *   `c4/`: C4 model diagrams (Context, Container, Component).
    *   `uml/`: Detailed UML diagrams.
        *   `class/`: UML Class diagrams for key data structures or modules.
        *   `sequence/`: UML Sequence diagrams illustrating important workflows.
*   **`docs/features/`**: Documentation related to specific features or implementation proposals (e.g., `fine_tuning_export/`).
