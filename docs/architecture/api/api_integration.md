# API Integration Documentation

This document provides comprehensive documentation for the Open WebUI backend API integration.

## API Overview

### Base URL
```
https://api.openwebui.com/v1
```

### Authentication
```python
class APIAuthentication:
    def __init__(self):
        self.auth_header = "Authorization"
        self.token_type = "Bearer"
        
    def get_auth_header(self, token: str) -> Dict[str, str]:
        """Generate authentication header."""
        return {
            self.auth_header: f"{self.token_type} {token}"
        }
```

## API Endpoints

### 1. Chat Endpoints

#### Chat Completion
```python
@router.post("/chat/completions")
async def chat_completion(
    request: ChatCompletionRequest,
    auth: AuthDependency
) -> ChatCompletionResponse:
    """
    Generate chat completion.
    
    Request:
    {
        "model": "string",
        "messages": [
            {
                "role": "user|assistant",
                "content": "string"
            }
        ],
        "temperature": float,
        "max_tokens": int,
        "stream": bool
    }
    
    Response:
    {
        "id": "string",
        "choices": [
            {
                "message": {
                    "role": "string",
                    "content": "string"
                },
                "finish_reason": "string"
            }
        ],
        "created": int,
        "model": "string"
    }
    """
```

#### Chat History
```python
@router.get("/chat/history")
async def get_chat_history(
    chat_id: str,
    auth: AuthDependency
) -> List[ChatMessage]:
    """
    Retrieve chat history.
    
    Response:
    [
        {
            "id": "string",
            "role": "string",
            "content": "string",
            "created_at": "datetime"
        }
    ]
    """
```

### 2. RAG Endpoints

#### Document Processing
```python
@router.post("/rag/documents")
async def process_document(
    file: UploadFile,
    auth: AuthDependency
) -> DocumentResponse:
    """
    Process document for RAG.
    
    Response:
    {
        "document_id": "string",
        "status": "string",
        "chunks": int,
        "created_at": "datetime"
    }
    """
```

#### Document Query
```python
@router.post("/rag/query")
async def query_documents(
    request: QueryRequest,
    auth: AuthDependency
) -> QueryResponse:
    """
    Query processed documents.
    
    Request:
    {
        "query": "string",
        "collection_id": "string",
        "top_k": int
    }
    
    Response:
    {
        "results": [
            {
                "document_id": "string",
                "content": "string",
                "score": float
            }
        ]
    }
    """
```

### 3. Model Management

#### Model Configuration
```python
@router.put("/models/{model_id}/config")
async def update_model_config(
    model_id: str,
    config: ModelConfig,
    auth: AuthDependency
) -> ModelConfigResponse:
    """
    Update model configuration.
    
    Request:
    {
        "temperature": float,
        "max_tokens": int,
        "top_p": float,
        "frequency_penalty": float,
        "presence_penalty": float
    }
    """
```

#### Model Deployment
```python
@router.post("/models/{model_id}/deploy")
async def deploy_model(
    model_id: str,
    deployment_config: DeploymentConfig,
    auth: AuthDependency
) -> DeploymentResponse:
    """
    Deploy model with configuration.
    
    Request:
    {
        "instance_type": "string",
        "replicas": int,
        "auto_scaling": bool
    }
    """
```

## Rate Limiting

### Implementation
```python
class RateLimiter:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.default_limit = 100
        self.default_window = 3600  # 1 hour
        
    async def check_rate_limit(
        self,
        key: str,
        limit: int = None,
        window: int = None
    ) -> bool:
        """Check if request is within rate limit."""
        current = await self.redis.incr(key)
        if current == 1:
            await self.redis.expire(key, window or self.default_window)
            
        return current <= (limit or self.default_limit)
```

### Rate Limit Headers
```python
class RateLimitHeaders:
    def __init__(self):
        self.limit_header = "X-RateLimit-Limit"
        self.remaining_header = "X-RateLimit-Remaining"
        self.reset_header = "X-RateLimit-Reset"
        
    def get_headers(
        self,
        limit: int,
        remaining: int,
        reset: int
    ) -> Dict[str, str]:
        """Generate rate limit headers."""
        return {
            self.limit_header: str(limit),
            self.remaining_header: str(remaining),
            self.reset_header: str(reset)
        }
```

## API Versioning

### Version Strategy
```python
class APIVersioning:
    def __init__(self):
        self.current_version = "v1"
        self.supported_versions = ["v1", "v2"]
        
    def validate_version(self, version: str) -> bool:
        """Validate API version."""
        return version in self.supported_versions
        
    def get_version_prefix(self, version: str) -> str:
        """Get version prefix for routes."""
        return f"/api/{version}"
```

### Version Migration
```python
class VersionMigration:
    def __init__(self):
        self.migrations = {
            "v1_to_v2": self.migrate_v1_to_v2
        }
        
    async def migrate_data(
        self,
        data: Any,
        from_version: str,
        to_version: str
    ) -> Any:
        """Migrate data between versions."""
        migration_key = f"{from_version}_to_{to_version}"
        if migration_key in self.migrations:
            return await self.migrations[migration_key](data)
        return data
```

## Webhook Integration

### Webhook Configuration
```python
class WebhookConfig:
    def __init__(self):
        self.endpoint = "string"
        self.secret = "string"
        self.events = ["chat.completed", "document.processed"]
        
    def validate_config(self) -> bool:
        """Validate webhook configuration."""
        return bool(self.endpoint and self.secret)
```

### Webhook Handler
```python
class WebhookHandler:
    def __init__(self, config: WebhookConfig):
        self.config = config
        self.client = AsyncHTTPClient()
        
    async def send_webhook(
        self,
        event: str,
        payload: Dict[str, Any]
    ) -> bool:
        """Send webhook event."""
        if event not in self.config.events:
            return False
            
        headers = self.generate_webhook_headers(event, payload)
        response = await self.client.post(
            self.config.endpoint,
            json=payload,
            headers=headers
        )
        
        return response.status_code == 200
```

## Error Handling

### API Errors
```python
class APIError(Exception):
    def __init__(
        self,
        message: str,
        code: str,
        status_code: int = 400
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)

class ErrorHandler:
    def __init__(self):
        self.error_mappings = {
            "invalid_input": (400, "Invalid input provided"),
            "unauthorized": (401, "Unauthorized access"),
            "forbidden": (403, "Access forbidden"),
            "not_found": (404, "Resource not found"),
            "rate_limit": (429, "Rate limit exceeded")
        }
        
    def handle_error(self, error: Exception) -> ErrorResponse:
        """Handle API errors."""
        if isinstance(error, APIError):
            return ErrorResponse(
                error=error.code,
                message=error.message,
                status_code=error.status_code
            )
            
        return ErrorResponse(
            error="internal_error",
            message="Internal server error",
            status_code=500
        )
```

## Best Practices

### 1. API Design
- Use RESTful conventions
- Implement proper versioning
- Provide clear documentation
- Use consistent error responses
- Implement proper validation

### 2. Security
- Use HTTPS for all endpoints
- Implement proper authentication
- Validate all inputs
- Sanitize all outputs
- Use rate limiting

### 3. Performance
- Implement caching
- Use compression
- Optimize response size
- Implement pagination
- Use async operations

### 4. Monitoring
- Log all requests
- Track response times
- Monitor error rates
- Track usage metrics
- Set up alerts

### 5. Testing
- Write unit tests
- Implement integration tests
- Test error scenarios
- Test rate limiting
- Test security measures 