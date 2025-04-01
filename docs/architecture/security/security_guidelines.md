# Security Guidelines

This document provides comprehensive security guidelines for the Open WebUI backend.

## Authentication and Authorization

### 1. Token Management

#### JWT Configuration
```python
# JWT settings
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Token generation
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt
```

#### Token Validation
```python
async def validate_token(token: str) -> bool:
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )
        return True
    except jwt.InvalidTokenError:
        return False
```

### 2. Role-Based Access Control (RBAC)

#### User Roles
```python
class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    READONLY = "readonly"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    role = Column(Enum(UserRole), default=UserRole.USER)
```

#### Permission Decorator
```python
def require_permission(required_role: UserRole):
    async def permission_checker(request: Request):
        user = request.state.user
        if user.role < required_role:
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions"
            )
        return True
    return permission_checker
```

## Data Security

### 1. Input Validation

#### Request Validation
```python
from pydantic import BaseModel, validator

class UserInput(BaseModel):
    content: str
    
    @validator("content")
    def validate_content(cls, v):
        if len(v) > 10000:
            raise ValueError("Content too long")
        return v.strip()
```

#### SQL Injection Prevention
```python
# Use parameterized queries
result = db.execute(
    "SELECT * FROM documents WHERE id = :id",
    {"id": document_id}
)
```

### 2. Data Encryption

#### Sensitive Data Encryption
```python
from cryptography.fernet import Fernet
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def encrypt_sensitive_data(data: str, key: str) -> str:
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(key.encode()))
    f = Fernet(key)
    return f.encrypt(data.encode()).decode()
```

#### API Key Storage
```python
# Hash API keys before storage
def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()
```

## Network Security

### 1. HTTPS Configuration

#### SSL/TLS Settings
```python
# SSL configuration
SSL_CERT_PATH = "/path/to/cert.pem"
SSL_KEY_PATH = "/path/to/key.pem"

# Force HTTPS
app = FastAPI()
app.middleware("https")
```

#### Security Headers
```python
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

### 2. Rate Limiting

#### Rate Limit Implementation
```python
from fastapi import HTTPException
from datetime import datetime, timedelta
from collections import defaultdict

class RateLimiter:
    def __init__(self, requests_per_minute: int):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
    
    def check_rate_limit(self, client_id: str) -> bool:
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)
        
        # Clean old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > minute_ago
        ]
        
        # Check rate limit
        if len(self.requests[client_id]) >= self.requests_per_minute:
            return False
        
        self.requests[client_id].append(now)
        return True
```

## File Security

### 1. File Upload Security

#### File Validation
```python
def validate_file(file: UploadFile) -> bool:
    # Check file size
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File too large"
        )
    
    # Check file type
    allowed_types = ["application/pdf", "text/plain", "application/msword"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type"
        )
    
    return True
```

#### Malware Scanning
```python
async def scan_file(file_path: str) -> bool:
    try:
        # Integrate with antivirus service
        result = await antivirus_service.scan(file_path)
        return result.is_clean
    except Exception as e:
        logger.error(f"Malware scan failed: {e}")
        return False
```

### 2. File Storage Security

#### Secure File Storage
```python
def store_file(file: UploadFile, user_id: str) -> str:
    # Generate unique filename
    filename = f"{uuid.uuid4()}_{file.filename}"
    
    # Store in secure location
    file_path = os.path.join(
        SECURE_STORAGE_PATH,
        user_id,
        filename
    )
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    
    return file_path
```

## Logging and Monitoring

### 1. Security Logging

#### Audit Logging
```python
class AuditLogger:
    def __init__(self):
        self.logger = logging.getLogger("audit")
    
    def log_access(self, user_id: str, action: str, resource: str):
        self.logger.info(
            f"Access: user={user_id}, action={action}, resource={resource}"
        )
    
    def log_security_event(self, event_type: str, details: dict):
        self.logger.warning(
            f"Security Event: type={event_type}, details={details}"
        )
```

#### Error Logging
```python
class SecurityErrorLogger:
    def __init__(self):
        self.logger = logging.getLogger("security")
    
    def log_auth_failure(self, user_id: str, reason: str):
        self.logger.warning(
            f"Auth Failure: user={user_id}, reason={reason}"
        )
    
    def log_rate_limit_exceeded(self, client_id: str):
        self.logger.warning(
            f"Rate Limit Exceeded: client={client_id}"
        )
```

### 2. Security Monitoring

#### Real-time Monitoring
```python
class SecurityMonitor:
    def __init__(self):
        self.alert_threshold = 5
        self.failed_attempts = defaultdict(int)
    
    def check_failed_attempts(self, user_id: str) -> bool:
        self.failed_attempts[user_id] += 1
        if self.failed_attempts[user_id] >= self.alert_threshold:
            self.send_alert(user_id)
            return False
        return True
    
    def send_alert(self, user_id: str):
        # Send alert to security team
        pass
```

## Best Practices

1. **Authentication**
   - Use strong password policies
   - Implement multi-factor authentication
   - Regular token rotation
   - Secure session management

2. **Authorization**
   - Implement least privilege principle
   - Regular permission audits
   - Role-based access control
   - API endpoint protection

3. **Data Protection**
   - Encrypt sensitive data
   - Secure API keys
   - Input validation
   - Output sanitization

4. **Network Security**
   - Use HTTPS only
   - Implement rate limiting
   - Configure security headers
   - Regular security updates

5. **File Security**
   - Validate file uploads
   - Scan for malware
   - Secure file storage
   - Access control

6. **Monitoring**
   - Comprehensive logging
   - Real-time alerts
   - Regular security audits
   - Incident response plan

7. **Compliance**
   - Follow security standards
   - Regular compliance checks
   - Document security procedures
   - Employee training 