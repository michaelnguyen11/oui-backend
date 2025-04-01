# Configuration Architecture

This document describes the configuration system used by the `oui-backend`, primarily defined in `open_webui/config.py`.

## Overview

The application utilizes a layered configuration system that allows settings to be defined via environment variables and potentially overridden or managed via a database-backed store. This provides flexibility for deployment (using environment variables) and runtime adjustments (using the database, likely via an admin interface).

## Core Mechanisms

1.  **Environment Variables (`open_webui/env.py`):** Environment variables serve as the primary source of configuration. They are loaded and parsed in `env.py`, providing typed access to settings defined externally (e.g., in `.env` files, Docker environment settings).

2.  **Database Backend (`Config` Model):**
    *   A SQLAlchemy model named `Config` is defined (`open_webui/config.py`), storing the application's configuration as a JSON blob in a dedicated database table.
    *   This allows configuration to be persisted and potentially modified at runtime without requiring application restarts (if the application reloads the config appropriately).
    *   Includes logic to migrate settings from a legacy `config.json` file into the database on first startup.

3.  **Layering (`PersistentConfig` & `AppConfig`):**
    *   The `PersistentConfig` class acts as a wrapper around individual configuration settings.
    *   It likely manages the relationship between a setting defined via an environment variable and its corresponding value in the database-stored JSON configuration, determining priority (typically environment variables override database values).
    *   The `AppConfig` class aggregates all the `PersistentConfig` instances, providing a unified access point (`app.state.config` in `main.py`) to the layered configuration values.

4.  **Loading and Access:**
    *   Configuration from the database is loaded at startup via `get_config()`.
    *   Functions like `get_config_value()` allow accessing specific nested configuration items.
    *   `save_config()` persists changes to the database and updates the runtime representation.

5.  **Migrations:** The configuration setup also triggers Alembic database migrations (`run_migrations()`) on startup to ensure the database schema is up-to-date.

## Key Configuration Areas

The `config.py` file, in conjunction with `env.py`, manages settings across numerous functional areas:

*   **Core Application:** Database connection (`DATABASE_URL`), data/cache directories, logging levels.
*   **Web UI:** Frontend name, favicon, default locale, CORS settings, JWT secrets/expiration, session cookie parameters, UI banners.
*   **Authentication:** Enabling auth, signup, login forms, API keys; default roles, user permissions; OAuth provider details (Google, Microsoft, GitHub, OIDC); LDAP settings; trusted proxy headers.
*   **LLM Backends:** Flags to enable/disable, base URLs, API keys for Ollama, OpenAI, and other compatible services.
*   **RAG Pipeline:** Vector DB type/connection; embedding engine/model; reranking model; chunking parameters; text splitters; retrieval parameters (top_k, threshold); document loaders (Tika, Azure AI); web search engine/keys; external service integrations.
*   **AI Features:** Image generation (engine, model, backends like Automatic1111/ComfyUI); Audio processing (STT/TTS engines, models, backends like Whisper/Azure); Code execution (engine, Jupyter details).
*   **Background Tasks:** Models and prompt templates for automated generation (titles, tags, etc.).
*   **Admin:** Admin email, feature flags for admin capabilities.
*   **WebSockets:** Enabling flag, manager type (Redis/local), Redis connection details.

## Summary

The configuration system provides a robust and flexible way to manage application settings. It prioritizes environment variables for deployment consistency while offering database persistence for runtime flexibility and potentially admin-driven changes. The system covers a wide range of parameters, controlling nearly every aspect of the application's behavior and integrations. 