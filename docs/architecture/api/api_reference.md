# API Reference and Integration Guide

This document provides comprehensive API documentation and integration guidelines for the Open WebUI backend.

## API Overview

### Base URL
```
http://localhost:3000/api/v1
```

### Authentication

All API endpoints require authentication using Bearer token:

```bash
Authorization: Bearer <your_access_token>
```

## Chat Endpoints

### 1. Chat Completion

```http
POST /chat/completions
```

**Request Body:**
```json
{
    "model": "gpt-3.5-turbo",
    "messages": [
        {
            "role": "user",
            "content": "Hello, how are you?"
        }
    ],
    "temperature": 0.7,
    "max_tokens": 1000,
    "stream": false
}
```

**Response:**
```json
{
    "id": "chatcmpl-123",
    "object": "chat.completion",
    "created": 1677652288,
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "I'm doing well, thank you!"
            },
            "finish_reason": "stop"
        }
    ],
    "usage": {
        "prompt_tokens": 9,
        "completion_tokens": 12,
        "total_tokens": 21
    }
}
```

### 2. Stream Chat Completion

```http
POST /chat/completions
```

**Request Body:**
```json
{
    "model": "gpt-3.5-turbo",
    "messages": [
        {
            "role": "user",
            "content": "Tell me a story"
        }
    ],
    "stream": true
}
```

**Response:**
Server-Sent Events (SSE) format:
```
data: {"choices":[{"delta":{"content":"Once"}}]}
data: {"choices":[{"delta":{"content":" upon"}}]}
data: {"choices":[{"delta":{"content":" a"}}]}
...
```

## RAG Endpoints

### 1. Document Processing

#### Upload Document
```http
POST /retrieval/process/file
```

**Request Body:**
```json
{
    "file": "<base64_encoded_file>",
    "collection_name": "my_documents",
    "metadata": {
        "source": "internal",
        "category": "technical"
    }
}
```

#### Process Web Content
```http
POST /retrieval/process/web/search
```

**Request Body:**
```json
{
    "query": "OpenAI API documentation",
    "collection_name": "web_content",
    "max_results": 5
}
```

### 2. Document Querying

#### Query Single Document
```http
POST /retrieval/query/doc
```

**Request Body:**
```json
{
    "doc_id": "doc123",
    "query": "What are the key features?",
    "top_k": 3
}
```

#### Query Collection
```http
POST /retrieval/query/collection
```

**Request Body:**
```json
{
    "collection_name": "my_documents",
    "query": "Find information about authentication",
    "top_k": 5,
    "use_hybrid_search": true
}
```

### 3. Configuration Management

#### Update Reranking Settings
```http
POST /retrieval/reranking/update
```

**Request Body:**
```json
{
    "model": "cross-encoder/ms-marco-TinyBERT-L-2-v2",
    "threshold": 0.7
}
```

#### Update Query Settings
```http
POST /retrieval/query/settings/update
```

**Request Body:**
```json
{
    "top_k": 5,
    "relevance_threshold": 0.7,
    "enable_hybrid_search": true
}
```

## Integration Examples

### 1. Python Integration

```python
import requests
import json

class OpenWebUIClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def chat_completion(self, messages: list, model: str = "gpt-3.5-turbo"):
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=self.headers,
            json={
                "model": model,
                "messages": messages,
                "stream": False
            }
        )
        return response.json()

    def process_document(self, file_path: str, collection_name: str):
        with open(file_path, "rb") as f:
            file_content = f.read()
        
        response = requests.post(
            f"{self.base_url}/retrieval/process/file",
            headers=self.headers,
            json={
                "file": file_content.hex(),
                "collection_name": collection_name
            }
        )
        return response.json()

    def query_collection(self, collection_name: str, query: str):
        response = requests.post(
            f"{self.base_url}/retrieval/query/collection",
            headers=self.headers,
            json={
                "collection_name": collection_name,
                "query": query,
                "top_k": 5
            }
        )
        return response.json()
```

### 2. JavaScript/TypeScript Integration

```typescript
class OpenWebUIClient {
    private baseUrl: string;
    private headers: Headers;

    constructor(baseUrl: string, apiKey: string) {
        this.baseUrl = baseUrl;
        this.headers = new Headers({
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
        });
    }

    async chatCompletion(messages: ChatMessage[], model: string = 'gpt-3.5-turbo') {
        const response = await fetch(`${this.baseUrl}/chat/completions`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({
                model,
                messages,
                stream: false
            })
        });
        return await response.json();
    }

    async processDocument(file: File, collectionName: string) {
        const fileContent = await file.arrayBuffer();
        const response = await fetch(`${this.baseUrl}/retrieval/process/file`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({
                file: Array.from(new Uint8Array(fileContent)),
                collection_name: collectionName
            })
        });
        return await response.json();
    }

    async queryCollection(collectionName: string, query: string) {
        const response = await fetch(`${this.baseUrl}/retrieval/query/collection`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({
                collection_name: collectionName,
                query,
                top_k: 5
            })
        });
        return await response.json();
    }
}
```

## Error Handling

### Common Error Codes

| Status Code | Description |
|-------------|-------------|
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid or missing token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server-side error |

### Error Response Format

```json
{
    "error": {
        "code": "rate_limit_exceeded",
        "message": "Too many requests. Please try again later.",
        "details": {
            "retry_after": 60
        }
    }
}
```

## Rate Limiting

### Limits

- Chat completions: 100 requests per minute
- Document processing: 50 requests per minute
- Collection queries: 200 requests per minute

### Rate Limit Headers

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1677652288
```

## Best Practices

1. **Authentication**
   - Store API keys securely
   - Rotate keys regularly
   - Use environment variables

2. **Error Handling**
   - Implement exponential backoff
   - Handle rate limits gracefully
   - Log errors appropriately

3. **Performance**
   - Use connection pooling
   - Implement caching
   - Batch requests when possible

4. **Security**
   - Use HTTPS only
   - Validate all inputs
   - Sanitize outputs

5. **Monitoring**
   - Track API usage
   - Monitor error rates
   - Set up alerts 