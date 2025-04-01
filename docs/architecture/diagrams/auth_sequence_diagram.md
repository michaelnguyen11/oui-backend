# Authentication and Authorization Sequence Diagrams

This document provides detailed sequence diagrams for the authentication and authorization system's key operations.

## 1. User Login Flow

```mermaid
sequenceDiagram
    participant Client
    participant AuthRouter
    participant AuthService
    participant TokenService
    participant Database
    participant Redis

    Client->>AuthRouter: POST /api/v1/auth/login
    AuthRouter->>AuthService: validate_credentials(username, password)
    AuthService->>Database: get_user_by_username()
    Database-->>AuthService: UserModel
    
    AuthService->>AuthService: verify_password()
    AuthService->>TokenService: generate_access_token()
    TokenService->>TokenService: create_jwt()
    TokenService-->>AuthService: AccessToken
    
    AuthService->>TokenService: generate_refresh_token()
    TokenService->>TokenService: create_jwt()
    TokenService-->>AuthService: RefreshToken
    
    AuthService->>Redis: store_refresh_token()
    AuthService-->>AuthRouter: AuthResponse
    AuthRouter-->>Client: 200 OK
```

## 2. API Key Generation Flow

```mermaid
sequenceDiagram
    participant Client
    participant AuthRouter
    participant AuthService
    participant KeyService
    participant Database

    Client->>AuthRouter: POST /api/v1/auth/api-key
    AuthRouter->>AuthService: get_verified_user()
    AuthService->>Database: get_user_by_id()
    Database-->>AuthService: UserModel
    
    AuthService->>KeyService: generate_api_key()
    KeyService->>KeyService: create_secure_key()
    KeyService->>KeyService: hash_key()
    KeyService-->>AuthService: ApiKey
    
    AuthService->>Database: store_api_key()
    AuthService-->>AuthRouter: ApiKeyResponse
    AuthRouter-->>Client: 200 OK
```

## 3. Token Refresh Flow

```mermaid
sequenceDiagram
    participant Client
    participant AuthRouter
    participant AuthService
    participant TokenService
    participant Redis

    Client->>AuthRouter: POST /api/v1/auth/refresh
    AuthRouter->>AuthService: validate_refresh_token()
    AuthService->>Redis: get_refresh_token()
    Redis-->>AuthService: TokenData
    
    AuthService->>TokenService: verify_token()
    TokenService-->>AuthService: Valid
    
    AuthService->>TokenService: generate_access_token()
    TokenService->>TokenService: create_jwt()
    TokenService-->>AuthService: NewAccessToken
    
    AuthService-->>AuthRouter: TokenResponse
    AuthRouter-->>Client: 200 OK
```

## 4. Role-Based Access Control Flow

```mermaid
sequenceDiagram
    participant Client
    participant AuthRouter
    participant AuthService
    participant RBACService
    participant Database

    Client->>AuthRouter: Protected Endpoint
    AuthRouter->>AuthService: get_verified_user()
    AuthService->>Database: get_user_by_id()
    Database-->>AuthService: UserModel
    
    AuthService->>RBACService: check_permissions()
    RBACService->>Database: get_user_roles()
    Database-->>RBACService: Roles[]
    
    RBACService->>RBACService: validate_permissions()
    RBACService-->>AuthService: HasAccess
    
    AuthService-->>AuthRouter: Authorized
    AuthRouter->>ProtectedEndpoint: Execute
    ProtectedEndpoint-->>Client: Response
```

## Component Interactions

### 1. Authentication
- Credential validation
- Token generation
- Session management
- Password verification

### 2. API Key Management
- Key generation
- Key storage
- Key validation
- Key revocation

### 3. Token Management
- Access token generation
- Refresh token handling
- Token validation
- Token storage

### 4. Authorization
- Role verification
- Permission checking
- Access control
- Policy enforcement

## Error Handling

1. **Authentication Errors**
   - Invalid credentials
   - Account locked
   - Session expired
   - Token invalid

2. **API Key Errors**
   - Key generation failed
   - Key validation failed
   - Key revoked
   - Rate limit exceeded

3. **Token Errors**
   - Token expired
   - Token invalid
   - Refresh failed
   - Token revoked

4. **Authorization Errors**
   - Insufficient permissions
   - Role not found
   - Policy violation
   - Access denied 