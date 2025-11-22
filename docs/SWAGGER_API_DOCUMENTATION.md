# Swagger/OpenAPI Documentation Implementation

## Overview

This document describes the implementation of Swagger/OpenAPI documentation for the Keycloak Auth Service API using `flask-smorest`.

## Implementation Details

### Library Choice: flask-smorest

**Why flask-smorest?**
- Modern Flask extension with built-in OpenAPI 3.0 support
- Automatic request/response validation using marshmallow schemas
- Clean decorator-based API documentation
- Built-in Swagger UI and ReDoc integration
- Better structured than alternatives like flasgger

### Dependencies Added

```
flask-smorest==0.42.3
marshmallow==3.20.1
```

### Key Components

#### 1. Schemas (`app/schemas.py`)
- **Request Schemas**: Validate incoming JSON data
- **Response Schemas**: Document API responses
- **Error Schema**: Standardized error responses

#### 2. Blueprint Configuration
All blueprints converted to `flask_smorest.Blueprint`:
- `auth_bp`: Authentication endpoints (`/auth/*`)
- `protected_bp`: Protected API endpoints (`/api/*`)
- `sso_bp`: SSO authentication endpoints (`/auth/sso/*`)

#### 3. Decorator Usage
Each endpoint uses appropriate decorators:
- `@bp.arguments(Schema)`: Request body validation
- `@bp.response(status_code, Schema)`: Response documentation
- Multiple response decorators for different status codes

## API Documentation Access

Once the service is running, access documentation at:

- **Swagger UI**: http://localhost:5000/swagger-ui
- **ReDoc**: http://localhost:5000/redoc  
- **OpenAPI Spec**: http://localhost:5000/openapi.json

## Documented Endpoints

### Authentication (`/auth/*`)

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/auth/login` | POST | Login with username/password | No |
| `/auth/refresh` | POST | Refresh access token | No |
| `/auth/logout` | POST | Logout and invalidate tokens | No |
| `/auth/validate` | POST | Validate access token | No |
| `/auth/userinfo` | GET | Get current user info | Yes |
| `/auth/register` | POST | Register new user | No |

### SSO Authentication (`/auth/sso/*`)

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/auth/sso/providers` | GET | List available SSO providers | No |
| `/auth/sso/login/<provider>` | GET | Get SSO login URL | No |
| `/auth/oauth/callback` | POST | Exchange OAuth code for tokens | No |

### Protected API (`/api/*`)

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/public` | GET | Public endpoint | No |
| `/api/protected` | GET | Protected endpoint | Yes (any role) |
| `/api/admin` | GET | Admin-only endpoint | Yes (admin role) |
| `/api/user-data` | GET | User data endpoint | Yes (user/admin role) |

## Schema Examples

### Login Request
```json
{
  "username": "testuser",
  "password": "password123"
}
```

### Login Response
```json
{
  "message": "Login successful",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "expires_in": 300,
  "refresh_expires_in": 1800,
  "token_type": "Bearer",
  "user_info": {
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "testuser",
    "email": "testuser@example.com",
    "roles": ["user"]
  }
}
```

### Registration Request
```json
{
  "username": "newuser",
  "email": "newuser@example.com", 
  "password": "SecurePass123",
  "firstName": "John",
  "lastName": "Doe"
}
```

### Error Response
```json
{
  "error": "Authentication failed",
  "details": "Invalid username or password"
}
```

## Authentication Documentation

### Bearer Token Authentication

Protected endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### Role-Based Access Control

Some endpoints require specific roles:
- **Admin endpoints**: Require `admin` role
- **User endpoints**: Require `user` or `admin` role
- **Protected endpoints**: Require any valid token

## Rate Limiting

The registration endpoint has rate limiting:
- **Limit**: 5 registrations per 15 minutes per IP address
- **Response**: 429 Too Many Requests when exceeded

## Testing the Documentation

### Manual Testing
1. Start the auth service: `python run.py`
2. Visit: http://localhost:5000/swagger-ui
3. Test endpoints directly from the Swagger UI

### Automated Testing
```bash
python test_swagger.py
```

## Benefits of This Implementation

1. **Automatic Validation**: Request data validated against schemas
2. **Interactive Documentation**: Test endpoints directly from Swagger UI
3. **Type Safety**: Marshmallow schemas provide runtime type checking
4. **Standardized Responses**: Consistent error and success response formats
5. **Developer Experience**: Clear API documentation for frontend developers
6. **API Versioning**: Built-in support for API versioning
7. **Export Options**: OpenAPI spec can be exported for code generation

## Production Considerations

1. **Security**: Consider disabling Swagger UI in production
2. **Performance**: Schema validation adds minimal overhead
3. **Maintenance**: Keep schemas in sync with actual API behavior
4. **Versioning**: Use API versioning for breaking changes

## Future Enhancements

1. **Authentication Schemes**: Add proper OpenAPI security schemes
2. **Examples**: Add more request/response examples
3. **Tags**: Group endpoints with tags for better organization
4. **Deprecation**: Mark deprecated endpoints
5. **External Docs**: Link to external documentation