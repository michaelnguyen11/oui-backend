# File Management Sequence Diagrams

This document provides detailed sequence diagrams for the file management system's key operations.

## 1. File Upload Flow

```mermaid
sequenceDiagram
    participant Client
    participant FileRouter
    participant FileService
    participant StorageService
    participant ValidationService
    participant Database

    Client->>FileRouter: POST /api/v1/files/upload
    FileRouter->>FileService: process_upload()
    FileService->>ValidationService: validate_file()
    ValidationService->>ValidationService: check_file_type()
    ValidationService->>ValidationService: check_file_size()
    ValidationService-->>FileService: ValidationResult
    
    FileService->>StorageService: store_file()
    StorageService->>StorageService: generate_unique_path()
    StorageService->>StorageService: save_file()
    StorageService-->>FileService: FileLocation
    
    FileService->>Database: create_file_record()
    Database-->>FileService: FileRecord
    
    FileService-->>FileRouter: FileResponse
    FileRouter-->>Client: 200 OK
```

## 2. File Processing Flow

```mermaid
sequenceDiagram
    participant Client
    participant FileRouter
    participant FileService
    participant ProcessingService
    participant StorageService
    participant Database

    Client->>FileRouter: POST /api/v1/files/{file_id}/process
    FileRouter->>FileService: process_file()
    FileService->>Database: get_file_record()
    Database-->>FileService: FileRecord
    
    FileService->>StorageService: retrieve_file()
    StorageService-->>FileService: FileContent
    
    FileService->>ProcessingService: process_content()
    ProcessingService->>ProcessingService: extract_metadata()
    ProcessingService->>ProcessingService: generate_preview()
    ProcessingService-->>FileService: ProcessedContent
    
    FileService->>Database: update_file_record()
    Database-->>FileService: UpdatedRecord
    
    FileService-->>FileRouter: ProcessingResponse
    FileRouter-->>Client: 200 OK
```

## 3. File Download Flow

```mermaid
sequenceDiagram
    participant Client
    participant FileRouter
    participant FileService
    participant StorageService
    participant Database
    participant Cache

    Client->>FileRouter: GET /api/v1/files/{file_id}/download
    FileRouter->>FileService: get_file()
    FileService->>Database: get_file_record()
    Database-->>FileService: FileRecord
    
    FileService->>Cache: check_file_cache()
    
    alt Cache Miss
        Cache-->>FileService: CacheMiss
        FileService->>StorageService: retrieve_file()
        StorageService-->>FileService: FileContent
        FileService->>Cache: cache_file()
    else Cache Hit
        Cache-->>FileService: FileContent
    end
    
    FileService-->>FileRouter: FileContent
    FileRouter-->>Client: 200 OK
```

## 4. File Deletion Flow

```mermaid
sequenceDiagram
    participant Client
    participant FileRouter
    participant FileService
    participant StorageService
    participant Database
    participant Cache

    Client->>FileRouter: DELETE /api/v1/files/{file_id}
    FileRouter->>FileService: delete_file()
    FileService->>Database: get_file_record()
    Database-->>FileService: FileRecord
    
    FileService->>StorageService: delete_file()
    StorageService->>StorageService: remove_file()
    StorageService-->>FileService: Success
    
    FileService->>Cache: invalidate_cache()
    Cache-->>FileService: CacheInvalidated
    
    FileService->>Database: delete_file_record()
    Database-->>FileService: Success
    
    FileService-->>FileRouter: DeletionResponse
    FileRouter-->>Client: 200 OK
```

## Component Interactions

### 1. File Upload
- File validation
- Storage management
- Database record creation
- Error handling

### 2. File Processing
- Content extraction
- Metadata generation
- Preview creation
- Record updates

### 3. File Download
- Cache management
- Storage retrieval
- Content delivery
- Access control

### 4. File Deletion
- Storage cleanup
- Cache invalidation
- Database cleanup
- Resource release

## Error Handling

1. **Upload Errors**
   - File size exceeded
   - Invalid file type
   - Storage full
   - Upload interrupted

2. **Processing Errors**
   - Content extraction failed
   - Preview generation failed
   - Metadata extraction failed
   - Processing timeout

3. **Download Errors**
   - File not found
   - Access denied
   - Storage error
   - Cache error

4. **Deletion Errors**
   - File locked
   - Storage error
   - Database error
   - Cache error 