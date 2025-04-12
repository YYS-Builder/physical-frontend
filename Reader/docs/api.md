# API Documentation

This document provides detailed information about the Reader API endpoints, request/response formats, and authentication.

## Base URL

```
http://localhost:8000/api
```

## Authentication

All API endpoints require authentication using JWT tokens.

### Obtaining a Token

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

### Using the Token

Include the token in the Authorization header:
```
Authorization: Bearer <token>
```

## Endpoints

### Authentication

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "name": "John Doe"
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

#### Refresh Token
```http
POST /auth/refresh
Authorization: Bearer <token>
```

### Documents

#### List Documents
```http
GET /documents
Authorization: Bearer <token>
```

Query Parameters:
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 10)
- `sort`: Sort field (default: created_at)
- `order`: Sort order (asc/desc)
- `search`: Search query
- `type`: Document type filter
- `status`: Document status filter

#### Get Document
```http
GET /documents/{id}
Authorization: Bearer <token>
```

#### Create Document
```http
POST /documents
Authorization: Bearer <token>
Content-Type: multipart/form-data

{
  "file": <file>,
  "title": "Document Title",
  "description": "Document Description",
  "type": "pdf",
  "tags": ["tag1", "tag2"]
}
```

#### Update Document
```http
PUT /documents/{id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Updated Title",
  "description": "Updated Description",
  "tags": ["tag1", "tag2", "tag3"]
}
```

#### Delete Document
```http
DELETE /documents/{id}
Authorization: Bearer <token>
```

### Collections

#### List Collections
```http
GET /collections
Authorization: Bearer <token>
```

#### Get Collection
```http
GET /collections/{id}
Authorization: Bearer <token>
```

#### Create Collection
```http
POST /collections
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Collection Name",
  "description": "Collection Description",
  "documents": [1, 2, 3]
}
```

#### Update Collection
```http
PUT /collections/{id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Updated Name",
  "description": "Updated Description",
  "documents": [1, 2, 3, 4]
}
```

#### Delete Collection
```http
DELETE /collections/{id}
Authorization: Bearer <token>
```

### Analytics

#### Get Reading Statistics
```http
GET /analytics/statistics
Authorization: Bearer <token>
```

Query Parameters:
- `start_date`: Start date (YYYY-MM-DD)
- `end_date`: End date (YYYY-MM-DD)

#### Get Reading Patterns
```http
GET /analytics/patterns
Authorization: Bearer <token>
```

Query Parameters:
- `start_date`: Start date (YYYY-MM-DD)
- `end_date`: End date (YYYY-MM-DD)

### User Profile

#### Get Profile
```http
GET /users/profile
Authorization: Bearer <token>
```

#### Update Profile
```http
PUT /users/profile
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Updated Name",
  "email": "updated@example.com"
}
```

#### Change Password
```http
PUT /users/password
Authorization: Bearer <token>
Content-Type: application/json

{
  "current_password": "current123",
  "new_password": "new123"
}
```

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message"
}
```

Common HTTP Status Codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 422: Validation Error
- 500: Internal Server Error

## Rate Limiting

API requests are limited to:
- 100 requests per minute for authenticated users
- 20 requests per minute for unauthenticated users

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1625097600
```

## WebSocket API

### Connection

```
ws://localhost:8000/ws
```

### Authentication

Send authentication message:
```json
{
  "type": "auth",
  "token": "<jwt_token>"
}
```

### Events

#### Document Processing Updates
```json
{
  "type": "processing_update",
  "document_id": 123,
  "status": "processing",
  "progress": 50
}
```

#### Notifications
```json
{
  "type": "notification",
  "id": 456,
  "title": "New Document",
  "message": "Document processing completed",
  "timestamp": "2023-01-01T12:00:00Z"
}
```

## SDKs and Libraries

### Python
```python
from reader_sdk import ReaderClient

client = ReaderClient(api_key="your_api_key")
documents = client.get_documents()
```

### JavaScript
```javascript
import { ReaderClient } from 'reader-sdk';

const client = new ReaderClient({
  apiKey: 'your_api_key'
});

const documents = await client.getDocuments();
```

## Support

For API support, contact:
- Email: support@reader.com
- Documentation: https://docs.reader.com
- GitHub Issues: https://github.com/your-username/reader/issues 