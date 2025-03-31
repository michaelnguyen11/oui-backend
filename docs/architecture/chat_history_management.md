# Chat History and Multi-User Management

This document describes how the `oui-backend` manages chat history and ensures data isolation between multiple users.

## Core Principles

1.  **User-Centric Data:** Every piece of core chat data is tied directly to a specific user.
    *   The `Chat` model (representing a conversation session) has a `user_id` column.
    *   The `Message` model (representing individual turns in a conversation) also has a `user_id` column, associating each message with its author.
    *   *Reference:* See `docs/uml_class_chat_messages.puml` for the detailed model structure.

2.  **Authentication Enforcement:** Access to chat data is gated by user authentication.
    *   API endpoints related to chats (`routers/chats.py`, etc.) use FastAPI dependencies like `Depends(get_verified_user)` (defined in `utils/auth.py`).
    *   This dependency ensures that only valid, logged-in users can access these endpoints. It retrieves the specific `UserModel` for the requesting user.

3.  **Data Access Layer Filtering:** The functions responsible for retrieving chat data consistently use the authenticated user's ID to filter database queries.
    *   Methods within `ChatTable` (e.g., `get_chat_list_by_user_id`) and `MessageTable` (e.g., `get_messages_by_channel_id`) explicitly filter results based on the `user_id` passed to them (which originates from the authenticated user).
    *   This prevents User A from accidentally or intentionally retrieving data belonging to User B.

4.  **Chat Representation:**
    *   Individual messages are stored as rows in the `message` table.
    *   The `Chat` model also contains a `chat: JSON` field. This likely stores a structured representation (e.g., a list of message objects) of the conversation within the main chat record itself, potentially used for efficiently loading the full conversation history for the UI. This field is updated as new messages are added.

## Summary

The backend ensures multi-user chat history management and isolation primarily through database schema design (associating all relevant records with a `user_id`) and strict enforcement of filtering based on the authenticated user during data retrieval operations in the API and data access layers. 