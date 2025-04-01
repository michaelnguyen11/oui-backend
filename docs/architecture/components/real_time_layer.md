# Real-time Layer Architecture (Socket.IO)

This document describes the real-time communication layer of the `oui-backend`, implemented using Socket.IO and located primarily in `open_webui/socket/main.py`. This layer enables features like live chat updates, user presence indicators, and real-time model usage tracking.

## Core Technology

*   **Library:** `python-socketio` is used to implement the Socket.IO protocol.
*   **Transport:** Primarily uses WebSockets (`transport=["websocket"]`) if enabled via `ENABLE_WEBSOCKET_SUPPORT`, otherwise falls back to HTTP long-polling.
*   **Integration:** The Socket.IO server is wrapped as an ASGI application (`socketio.ASGIApp`) and mounted at the `/ws` path within the main FastAPI application (`open_webui/main.py`).

## Scaling & State Management

*   **Multi-Instance Support:** The architecture supports running multiple backend instances.
*   **Redis Backend (Optional):** If `WEBSOCKET_MANAGER` is configured to `"redis"`, `socketio.AsyncRedisManager` is used. This allows different backend instances to communicate and broadcast events to clients connected to any instance.
*   **Shared State:** When Redis is enabled, application state relevant to connected clients is stored in Redis using custom `RedisDict` wrappers (`open_webui/socket/utils.py`):
    *   `SESSION_POOL`: Maps Socket.IO session IDs (`sid`) to authenticated user information.
    *   `USER_POOL`: Maps user IDs to a list of their currently connected session IDs.
    *   `USAGE_POOL`: Tracks which models are actively being used by which sessions, with timestamps.
*   **Locking:** A `RedisLock` is used to prevent race conditions during the periodic cleanup of the `USAGE_POOL`.
*   **Local State (Fallback):** If Redis is not configured, standard Python dictionaries are used for state management, suitable only for single-instance deployments.

## Key Functionality & Events

1.  **Connection & Authentication (`connect` event):**
    *   Clients connect to the `/ws/socket.io` endpoint.
    *   Authentication is performed using a JWT token provided in the connection `auth` data, validated via `decode_token`.
    *   Authenticated user and session information is stored in `SESSION_POOL` and `USER_POOL`.
    *   The server emits initial state information (`user-list`, `usage`) to the newly connected client.

2.  **Room Management (`user-join`, `join-channels` events):**
    *   Users are automatically joined to Socket.IO rooms based on their associated channels (e.g., `channel:{channel_id}`) upon connection or explicit request.
    *   This allows for targeted broadcasting of events only to relevant users (e.g., sending a new message only to users in that specific chat channel).

3.  **Event Broadcasting (`channel-events`, general emits):**
    *   The server defines handlers for specific events sent by clients (e.g., `usage`).
    *   It also broadcasts events to clients, often targeted to specific rooms (e.g., sending new message notifications to a channel room).
    *   Helper functions (`get_event_emitter`, `get_event_call`) are likely provided to allow other backend modules (like chat processing logic) to trigger WebSocket events without direct dependency on the `sio` object.

4.  **Presence & Usage Tracking:**
    *   `USER_POOL` implicitly tracks online users. The list of keys (`user_ids`) is broadcast via the `user-list` event upon connection/disconnection.
    *   `USAGE_POOL` tracks active model usage based on client `usage` events and is periodically cleaned (`periodic_usage_pool_cleanup`). The list of active models is broadcast via the `usage` event.

5.  **Disconnection (`disconnect` event):**
    *   When a client disconnects, their `sid` is removed from `SESSION_POOL`, `USER_POOL`, and `USAGE_POOL`.
    *   Updated `user-list` and `usage` information is broadcast to remaining clients.

## Summary

The real-time layer provides essential bidirectional communication capabilities using Socket.IO. It integrates seamlessly with the FastAPI application and supports scaling through Redis. Authentication, room-based broadcasting, presence tracking, and model usage monitoring are key features handled by this component, enabling a dynamic and interactive user experience. 