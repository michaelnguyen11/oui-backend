# Deep Dive: API Routers (FastAPI)

This document provides a more detailed explanation of how API Routers work in the `oui-backend`, using FastAPI. It builds upon the overview in `docs/api_routers.md`.

## What is Routing?

At its core, routing is the mechanism by which the web server determines which piece of code should handle an incoming request based on its URL path (e.g., `/api/v1/chats/123`) and HTTP method (e.g., `GET`, `POST`, `DELETE`).

FastAPI uses decorators (`@router.get`, `@router.post`, etc.) attached to Python functions to define these routes.

## Modular Routing with `APIRouter`

Instead of defining all possible routes in the main `open_webui/main.py` file, `oui-backend` uses FastAPI's `APIRouter` to organize related endpoints into separate files within the `open_webui/routers/` directory (e.g., `chats.py`, `users.py`, `retrieval.py`).

*   **Organization:** Each file handles a specific domain or feature set (e.g., all chat-related operations are in `chats.py`).
*   **Inclusion:** In `main.py`, these routers are included into the main `FastAPI` application using `app.include_router(chats.router, prefix="/api/v1/chats", tags=["chats"])`.
    *   `prefix`: Automatically adds `/api/v1/chats` to the beginning of all routes defined within `chats.py`. So, `@router.get("/")` inside `chats.py` actually becomes `/api/v1/chats/`.
    *   `tags`: Used for grouping endpoints in the automatic API documentation (like Swagger UI).

## Anatomy of a Router Endpoint (Example from `chats.py`)

Let's look at a simplified structure of an endpoint definition:

```python
# open_webui/routers/chats.py
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from open_webui.utils.auth import get_verified_user # Dependency for auth
from open_webui.models.chats import ChatResponse, ChatForm, Chats # Models & Data Access

# 1. Create Router instance
router = APIRouter()

# 2. Define Request Body Model (if needed)
class NewChatData(BaseModel):
    # Fields expected in the POST request body
    initial_prompt: str
    # ... other fields

# 3. Define Endpoint using Decorator
@router.post("/new", response_model=ChatResponse) # Path relative to prefix, expected response type
# 4. Define Handler Function with Type Hinting & Dependencies
async def create_new_chat(
    form_data: ChatForm, # Request Body, validated by Pydantic
    user = Depends(get_verified_user) # Dependency Injection for Authentication
):
    # 5. Function Body - Orchestration Logic
    try:
        # Call data access layer, passing authenticated user ID and validated form data
        new_chat = Chats.insert_new_chat(user.id, form_data)

        if not new_chat:
            raise HTTPException(status_code=500, detail="Failed to create chat")

        # 6. Return Data (matching response_model)
        # FastAPI automatically converts the ChatModel to the ChatResponse Pydantic model
        return new_chat
    except Exception as e:
        # Handle errors
        raise HTTPException(status_code=400, detail=f"Error: {e}")

```

**Key Steps in Handling a Request:**

1.  **Request Arrives:** A client (like the Frontend SPA) sends an HTTP request (e.g., `POST /api/v1/chats/new` with a JSON body).
2.  **FastAPI Routing:** FastAPI matches the path and method (`POST /api/v1/chats/new`) to the `@router.post("/new")` decorator in `chats.py`.
3.  **Dependency Injection:** Before executing `create_new_chat`, FastAPI runs the dependencies. It calls `get_verified_user()`.
    *   `get_verified_user` inspects the request's headers/cookies for a token.
    *   It validates the token and fetches the user details.
    *   If valid, it returns the `UserModel` object, which FastAPI injects as the `user` argument. If invalid, it raises an `HTTPException`, stopping the process.
4.  **Request Body Validation:** FastAPI takes the JSON body from the request and uses the `ChatForm` type hint to validate its structure and types using Pydantic. If validation fails, it automatically returns a 422 Unprocessable Entity error. The validated data is passed as the `form_data` argument.
5.  **Endpoint Execution:** The `create_new_chat` function body runs.
    *   It uses the injected `user.id` and the validated `form_data`.
    *   It calls the data access layer (`Chats.insert_new_chat`) to perform the database operation.
    *   It handles potential errors raised by the data access layer.
6.  **Response Handling:**
    *   The function returns the `new_chat` object (a `ChatModel`).
    *   Because `response_model=ChatResponse` is set in the decorator, FastAPI automatically validates that the returned data conforms to the `ChatResponse` model and serializes it into a JSON response body.
    *   FastAPI sends the HTTP response (e.g., 200 OK with the JSON body) back to the client.

**In Summary:** API Routers are the entry points for standard HTTP requests. They use FastAPI's features for path matching, dependency injection (crucial for auth), request validation (Pydantic), and response formatting to connect incoming requests to the appropriate backend logic and database operations. 