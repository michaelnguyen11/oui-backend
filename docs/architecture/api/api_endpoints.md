# API Endpoints

This document details the API endpoints available in the Open WebUI backend.

## Chat Endpoints

### Chat Completions

#### `POST /api/chat/completions`
- **Description**: Send chat messages and receive completions
- **Authentication**: Bearer token required
- **Request Body**:
  ```json
  {
    "model": "model-name",
    "messages": [
      {
        "role": "user",
        "content": "message content"
      }
    ]
  }
  ```
- **Response**: Streaming response with chat completions

## RAG Endpoints

### File Management

#### `POST /api/v1/files/`
- **Description**: Upload files for RAG processing
- **Authentication**: Bearer token required
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `file`: File to upload
- **Response**: File upload confirmation

#### `POST /api/v1/knowledge/{id}/file/add`
- **Description**: Add files to a knowledge collection
- **Authentication**: Bearer token required
- **Parameters**:
  - `id`: Knowledge collection ID
  - `file`: File to add
- **Response**: File addition confirmation

### Document Processing

#### `POST /api/v1/retrieval/process/file`
- **Description**: Process uploaded files for RAG
- **Authentication**: Bearer token required
- **Parameters**:
  - `file`: File to process
  - `collection_name`: Target collection name
- **Response**: Processing status and results

#### `POST /api/v1/retrieval/process/web/search`
- **Description**: Process web search results for RAG
- **Authentication**: Bearer token required
- **Parameters**:
  - `query`: Search query
  - `collection_name`: Target collection name
- **Response**: Search results and processing status

### Querying

#### `POST /api/v1/retrieval/query/doc`
- **Description**: Query a specific document
- **Authentication**: Bearer token required
- **Parameters**:
  - `collection_name`: Document collection name
  - `query`: Search query
  - `k`: Number of results (optional)
  - `r`: Relevance threshold (optional)
- **Response**: Retrieved document chunks

#### `POST /api/v1/retrieval/query/collection`
- **Description**: Query multiple collections
- **Authentication**: Bearer token required
- **Parameters**:
  - `collection_names`: List of collection names
  - `query`: Search query
  - `k`: Number of results (optional)
  - `r`: Relevance threshold (optional)
- **Response**: Retrieved document chunks from all collections

### Configuration

#### `POST /api/v1/retrieval/reranking/update`
- **Description**: Update reranking model configuration
- **Authentication**: Admin user required
- **Parameters**:
  - `reranking_model`: New reranking model name
- **Response**: Updated configuration status

#### `POST /api/v1/retrieval/query/settings/update`
- **Description**: Update query settings
- **Authentication**: Admin user required
- **Parameters**:
  - `template`: RAG template
  - `k`: Number of results
  - `r`: Relevance threshold
  - `hybrid`: Enable hybrid search
- **Response**: Updated settings status

## Usage Examples

### Python Example: Chat Completion

```python
import requests

def chat_with_model(token):
    url = 'http://localhost:3000/api/chat/completions'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {
        "model": "model-name",
        "messages": [
            {
                "role": "user",
                "content": "Why is the sky blue?"
            }
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()
```

### Python Example: File Upload

```python
import requests

def upload_file(token, file_path):
    url = 'http://localhost:3000/api/v1/files/'
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json'
    }
    files = {'file': open(file_path, 'rb')}
    response = requests.post(url, headers=headers, files=files)
    return response.json()
```

## Best Practices

1. **Authentication**
   - Always include Bearer token in requests
   - Use secure token storage and transmission
   - Implement proper token refresh mechanisms

2. **Error Handling**
   - Check response status codes
   - Handle rate limiting gracefully
   - Implement retry logic for failed requests

3. **Performance**
   - Use appropriate batch sizes
   - Implement request caching where possible
   - Monitor API usage and limits

4. **Security**
   - Use HTTPS for all requests
   - Validate input data
   - Implement proper access controls

5. **Documentation**
   - Keep API documentation up to date
   - Include example requests and responses
   - Document rate limits and quotas 