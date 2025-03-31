# Database Layer Architecture

This document describes the architecture of the database layer in the `oui-backend` application.

## Core Technologies

*   **ORM:** SQLAlchemy is used as the primary Object-Relational Mapper for defining data models and interacting with the database.
*   **Migrations (SQLAlchemy):** Alembic is used to manage database schema migrations for SQLAlchemy models. Configuration is found in `alembic.ini` and migration scripts reside in `open_webui/migrations/`.
*   **Migrations (Peewee):** The application *also* runs Peewee migrations during initialization (`open_webui/internal/db.py` calls `handle_peewee_migration`), using migration scripts from `open_webui/internal/migrations`. This suggests a potential legacy system or a specific component managed by Peewee.

## Components

1.  **SQLAlchemy Models (`open_webui/models/`):**
    *   Each file in this directory (e.g., `users.py`, `chats.py`, `messages.py`) defines a logical group of database tables.
    *   Models inherit from `Base = declarative_base()` defined in `open_webui/internal/db.py`.
    *   Standard SQLAlchemy `Column` types are used, along with a custom `JSONField` (defined in `db.py`) for storing JSON data in text columns.

2.  **Pydantic Models (Defined alongside SQLAlchemy models):**
    *   Pydantic models (e.g., `UserModel`, `ChatModel`) are often defined in the same files as their SQLAlchemy counterparts.
    *   They serve as Data Transfer Objects (DTOs) and are used for API request/response validation and serialization, providing a clear contract between the API layer and the database layer.

3.  **Database Connection & Session Management (`open_webui/internal/db.py`):**
    *   **Engine:** A SQLAlchemy engine (`create_engine`) is created based on the `DATABASE_URL` environment variable. It supports connection pooling (`QueuePool` or `NullPool`) for performance and reliability (`pool_pre_ping`).
    *   **Session Factory:** `sessionmaker` (`SessionLocal`) is configured, bound to the engine.
    *   **Scoped Session:** A thread-local session (`Session = scoped_session(SessionLocal)`) is provided for safe use in the web server environment.
    *   **Session Context Manager (`get_db`):** A context manager (`with get_db() as db: ...`) provides a standard, safe way to acquire and release database sessions within data access code.

4.  **Data Access Layer (Pattern in `models/*.py`):**
    *   A common pattern is to have a dedicated class (e.g., `UsersTable`, `ChatsTable`) within each model file.
    *   These classes encapsulate the CRUD (Create, Read, Update, Delete) operations for the corresponding SQLAlchemy models.
    *   Methods within these classes use the `get_db` context manager to interact with the database via the SQLAlchemy session. This keeps database interaction logic separate from the API endpoint logic.

## Workflow

1.  **Initialization:**
    *   Peewee migrations are run (`handle_peewee_migration`).
    *   The SQLAlchemy engine and session factories are created.
2.  **Request Handling:**
    *   An API router function needs database access.
    *   It typically calls a method on a data access class (e.g., `UsersTable().get_user_by_id(...)`).
    *   The data access method uses `with get_db() as db:` to get a session.
    *   SQLAlchemy queries are executed using the session (`db.query(...)`, `db.add(...)`, etc.).
    *   Data might be converted between SQLAlchemy models and Pydantic models.
    *   The `commit_session_after_request` middleware ensures changes are committed after the request completes successfully.
3.  **Schema Changes:**
    *   Developers use Alembic commands (`alembic revision --autogenerate`, `alembic upgrade head`) to generate and apply schema changes based on modifications to the SQLAlchemy models in `open_webui/models/`.

## Summary

The database layer relies primarily on SQLAlchemy for ORM and Alembic for migrations, following standard practices for session management and data access encapsulation. The presence of an initial Peewee migration step is a notable detail indicating potential historical context or specific requirements. Pydantic models play a key role in data validation and serialization between the database and API layers. 